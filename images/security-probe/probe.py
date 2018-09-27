#!/usr/bin/env python

"""probe.py

The probe is designed to run as an OpenShift Job, monitor a service location
for a specific response and then terminate that service if the response
does not comply with expectations. The service (part of a DeploymentConfig)
is terminated by setting its 'replicas' value to zero and then waiting, for
a short period of time, until the service stops responding.

The behaviour of the application is controlled by a number of
'required' environment variables: -

PROBE_LOCATION          The rest location to probe.
                        This is typically a path and service
                        (rather than a route) endpoint.

PROBE_OC_PASSWORD       The OpenShift user's password

PROBE_MAILGUBN_LOGIN    The Mailgun account login.

PROBE_MAILGUBN_PASSWORD The Mailgun account password.

PROBE_NAMESPACE         The name of the deployment's namespace.

PROBE_NAMESPACE_H       The human name of the deployment's namespace.
                        For use in email transmissions.

And a number of 'optional' environment variables: -

PROBE_DEPLOYMENT        The name of the deployment that should be scaled-down
                        on probe failure.
                        (default 'web')

PROBE_OC_HOST           A valid OpenShift host
                        (default 'openshift.xchem.diamond.ac.uk')

PROBE_OC_USER           A valid OpenShift host user
                        (default 'admin')

PROBE_PERIOD_M          The period between probes (minutes)
                        (default 5)

PROBE_RECIPIENTS        A comma-separated list of email recipients.
                        This is optional, if not provided no email will be
                        sent.

PROBE_THRESHOLD         The number of failures after which
                        the service will be suspended.
                        (default 2)

This Job may also terminate if there in an unrecoverable
error condition whereby it will log the condition but exit with
a code of 0 to avoid being re-spawned by OpenShift.
"""

from email.mime.text import MIMEText
from datetime import datetime
import os
import requests
import smtplib
import sys
import subprocess
import time

# Required environment variables

LOCATION_ENV = 'PROBE_LOCATION'
LOCATION = os.environ.get(LOCATION_ENV)

DEPLOYMENT_ENV = 'PROBE_DEPLOYMENT'
DEPLOYMENT = os.environ.get(DEPLOYMENT_ENV, 'web')

NAMESPACE_ENV = 'PROBE_NAMESPACE'
NAMESPACE = os.environ.get(NAMESPACE_ENV)

NAMESPACE_H_ENV = 'PROBE_NAMESPACE_H'
NAMESPACE_H = os.environ.get(NAMESPACE_H_ENV)

OC_PASSWORD = os.environ.get('PROBE_OC_PASSWORD')

MAILGUN_LOGIN = os.environ.get('PROBE_MAILGUN_LOGIN')
MAILGUN_PASSWORD = os.environ.get('PROBE_MAILGUN_PASSWORD')

# Optional environment variables

PERIOD_M_ENV = 'PROBE_PERIOD_M'
PERIOD_M = os.environ.get(PERIOD_M_ENV, '5')

RECIPIENTS_ENV = 'PROBE_RECIPIENTS'
RECIPIENTS = os.environ.get(RECIPIENTS_ENV)

THRESHOLD_ENV = 'PROBE_THRESHOLD'
THRESHOLD = os.environ.get(THRESHOLD_ENV, '2')

OC_HOST = os.environ.get('PROBE_OC_HOST', 'openshift.xchem.diamond.ac.uk')
OC_USER = os.environ.get('PROBE_OC_USER', 'admin')

# SMTP (Mailgun) details...
MAILGUN_ADDR = 'smtp.mailgun.org'
MAILGUN_PORT = 587

# The email address of the Security Probe
PROBE_EMAIL = 'Security Probe <dls.security.probe@informaticsmatters.com>'

# The period of time to pause, once we're initialised,
# prior to entering the probe loop
PRE_PROBE_DELAY_S = 10.0

# Timeout of the probe call
PROBE_TIMEOUT_S = 4.0

# The time (in seconds) to wait after suspending the
# service to wait for a loss of response.
POST_TERMINATE_PERIOD_S = 120
# The polling period for the probe after terminating.
POST_TERMINATE_PROBE_PERIOD_S = 5


def error(msg):
    """Prints the supplied error message and exists (cleanly).

    :param msg: A short error message
    :type msg: ``String``
    """
    message('ERROR: %s' % msg)
    sys.exit(0)


def warning(msg):
    """Prints the supplied warning message.

    :param msg: A short message
    :type msg: ``String``
    """
    message('WARNING: %s' % msg)


def message(msg):
    """Prints a message

    :param msg: The message
    :type msg: ``String``
    """
    print('-) [%s] %s' % (datetime.now(), msg))


def email_warning():
    """Sends an email, driven by the first probe failure.

    This email delivers a warning that the first probe attempt has
    failed. Another email will come when the probe fails a second time.
    """
    # Do nothing if no recipients
    if not RECIPIENTS:
        warning('Skipping email (no recipients)')
        return

    msg = MIMEText("The Fragalysis %s Project's Security Probe"
                   " has detected an initial failure.\n\n"
                   "The Security Probe will run again in %s minutes.\n\n"
                   "After %s failures (this counts as one)"
                   " the %s service will be suspended."
                   % (NAMESPACE_H, PERIOD_M, THRESHOLD, NAMESPACE_H),
                   _charset='utf-8')

    msg['Subject'] = 'Security Probe Failure' \
                     ' - Fragalysis %s Project' \
                     ' - First Event' % NAMESPACE_H
    msg['From'] = PROBE_EMAIL
    msg['To'] = RECIPIENTS

    smtp = smtplib.SMTP(MAILGUN_ADDR, MAILGUN_PORT)
    rv = smtp.login(MAILGUN_LOGIN, MAILGUN_PASSWORD)
    if rv[0] == 235:
        smtp.sendmail(PROBE_EMAIL,
                      RECIPIENTS.split(','),
                      msg.as_string())
    smtp.quit()

    message('Sent warning email')


def email_suspension():
    """Sends an email, driven by the final probe failure.

    This email delivers a warning that the final security probe attempt has
    failed and the probed service is being shutdown.
    """
    # Do nothing if no recipients
    if not RECIPIENTS:
        warning('Skipping email (no recipients)')
        return

    msg = MIMEText("The Fragalysis %s Project's Security Probe"
                   " has detected too many failures.\n\n"
                   "The service is now being suspended.\n\n"
                   "You should check the service implementation"
                   " and deploy a new working solution."
                   % NAMESPACE_H,
                   _charset='utf-8')

    msg['Subject'] = 'Security Probe Failure' \
                     ' - Fragalysis %s Project' \
                     ' - Service Suspended' % NAMESPACE_H
    msg['From'] = PROBE_EMAIL
    msg['To'] = RECIPIENTS

    smtp = smtplib.SMTP(MAILGUN_ADDR, MAILGUN_PORT)
    rv = smtp.login(MAILGUN_LOGIN, MAILGUN_PASSWORD)
    if rv[0] == 235:
        smtp.sendmail(PROBE_EMAIL,
                      RECIPIENTS.split(','),
                      msg.as_string())
    smtp.quit()

    message('Sent suspension email')


def email_suspension_failure():
    """Sends an email, driven by the failure to suspend the service.

    This email delivers a warning that the suspension of the probed
    service failed and there is a possibility that it is still running
    and vulnerable.
    """
    # Do nothing if no recipients
    if not RECIPIENTS:
        warning('Skipping email (no recipients)')
        return

    msg = MIMEText("The Fragalysis %s Project's Service"
                   " has failed to respond to a suspension request."
                   " This is unexpected and leaves the service deployed"
                   " and vulnerable.\n\n"
                   "Please seek the urgent advice of a"
                   " cluster administrator."
                   % NAMESPACE_H,
                   _charset='utf-8')

    msg['Subject'] = 'Security Probe Failure' \
                     ' - Fragalysis %s Project' \
                     ' - Service Suspension Failure' % NAMESPACE_H
    msg['From'] = PROBE_EMAIL
    msg['To'] = RECIPIENTS

    smtp = smtplib.SMTP(MAILGUN_ADDR, MAILGUN_PORT)
    rv = smtp.login(MAILGUN_LOGIN, MAILGUN_PASSWORD)
    if rv[0] == 235:
        smtp.sendmail(PROBE_EMAIL,
                      RECIPIENTS.split(','),
                      msg.as_string())
    smtp.quit()

    message('Sent suspension failure email')


def probe():
    """Probes the service, returning True if the response
    is as if expected:
    """
    # Probe the location (REST GET)
    # with a 4-second timeout
    try:
        resp = requests.get(LOCATION,
                            headers={'accept': 'application/json'},
                            timeout=PROBE_TIMEOUT_S)
    except:
        # Any failure will be logged
        # but ignored.
        pass

    # Assume success
    ret_val = True
    # If successful, check the content.
    # the 'count' must be '0'
    if resp and resp.status_code == 200:
        if 'count' in resp.json():
            count = resp.json()['count']
            if count:
                ret_val = False
                warning('Received probe "count" value of %d' % count)
        else:
            # Count not in the response. Odd?
            warning('"count" not in the response')
    else:
        if resp:
            warning('Got status %d' % resp.status_code)
        else:
            warning('Got no response from location')

    return ret_val


# Pre-flight checks...
#
# Must have OC host, user and password
if not OC_HOST:
    error('An OC host must be supplied')
if not OC_USER:
    error('An OC user must be supplied')
if not OC_PASSWORD:
    error('An OC user password must be supplied')
# A namespace must be provided
if not NAMESPACE:
    error('The %s environment variable is not defined' % NAMESPACE)
# A location must be provided.
if not LOCATION:
    error('The %s environment variable is not defined' % LOCATION_ENV)
# A deployment (behind the service we're monitoring) must be provided.
if not DEPLOYMENT:
    error('The %s environment variable is not defined' % DEPLOYMENT_ENV)
# Must have mailgun credentials
if not MAILGUN_LOGIN:
    error('The mailgun login is not defined')
if not MAILGUN_PASSWORD:
    error('The mailgun password is not defined')

# Conversions.
# Period must be a number
try:
    period_s_int = int(PERIOD_M) * 60
except ValueError:
    error('%s is not a number (%s)' % (PERIOD_M_ENV, PERIOD_M))
# Threshold must be a number
try:
    threshold_int = int(THRESHOLD)
except ValueError:
    error('%s is not a number (%s)' % (THRESHOLD_ENV, THRESHOLD))

# Ready to go...
#
# Log startup conditions, pause for a moment
# then enter the probe/sleep loop

message('LOCATION="%s"' % LOCATION)
message('PERIOD_M=%s' % PERIOD_M)
message('THRESHOLD=%s' % THRESHOLD)

message('In pre-probe delay...')
time.sleep(PRE_PROBE_DELAY_S)

message('Probing...')
failure_count = 0
failed = False
while not failed:

    # Probe (and deal with failure)
    if not probe():
        failure_count += 1
        message('Probe failed (%d/%d)' % (failure_count, threshold_int))
        if failure_count == 1:
            email_warning()
        elif failure_count >= threshold_int:
            message('Reached failure threshold')
            failed = True

    # If not failed,
    # sleep prior to the next attempt...
    if not failed:
        time.sleep(period_s_int)

# If we get here the probe has failed!
# We must send an email.

message('Suspending the service...')

# Suspend the service.
# To suspend the service we scale the DeploymentConfig
# so that the number of replicas is 0...

# Login
#
message('Logging in to OpenShift...')
cmd = 'oc login %s -u %s -p %s' % (OC_HOST, OC_USER, OC_PASSWORD)
result = subprocess.run(cmd.split(),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
suspended = False
if result.returncode:
    # Login failed!
    message('Login failed!')
else:
    message('Logged in')

    # Project
    #
    message('Switching namespace...')
    cmd = 'oc project %s' % NAMESPACE
    result = subprocess.run(cmd.split(),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    if result.returncode:
        # Project movement failed!
        message('Project failed!')
    else:
        message('Switched')

        # Scale
        #
        message('Suspending service...')
        cmd = 'oc scale dc %s --replicas=0' % DEPLOYMENT
        result = subprocess.run(cmd.split(),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if result.returncode:
            # The scaling command failed!
            message('Suspension failed!')
        else:
            message('Suspended')
            email_suspension()

            # Continue to probe until success
            #
            message('Waiting for service termination...')
            waited_s = 0
            waited_long_enough = False
            while not waited_long_enough:
                if probe():
                    suspended = True
                    waited_long_enough = True
                    message('Terminated')
                else:
                    time.sleep(POST_TERMINATE_PROBE_PERIOD_S)
                    waited_s += POST_TERMINATE_PROBE_PERIOD_S
                    if waited_s >= POST_TERMINATE_PERIOD_S:
                        waited_long_enough = True

# If we failed to suspend the service...
if not suspended:
    warning('Service failed to respond to suspension!')
    email_suspension_failure()

# We leave without an error.
# The Job will terminate until we're run again.
message("That's all Folks!")
