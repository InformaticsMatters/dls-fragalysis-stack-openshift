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
from enum import Enum
from datetime import datetime
import os
import requests
import smtplib
import sys
import subprocess
import time

# Required environment variables

LOCATION = os.environ.get('PROBE_LOCATION')
DEPLOYMENT = os.environ.get('PROBE_DEPLOYMENT', 'web')
NAMESPACE = os.environ.get('PROBE_NAMESPACE')
NAMESPACE_H = os.environ.get('PROBE_NAMESPACE_H')
OC_PASSWORD = os.environ.get('PROBE_OC_PASSWORD')
MAILGUN_LOGIN = os.environ.get('PROBE_MAILGUN_LOGIN')
MAILGUN_PASSWORD = os.environ.get('PROBE_MAILGUN_PASSWORD')

# Optional environment variables

PERIOD_M = os.environ.get('PROBE_PERIOD_M', '5')
RECIPIENTS = os.environ.get('PROBE_RECIPIENTS')
THRESHOLD = os.environ.get('PROBE_THRESHOLD', '2')

OC_HOST = os.environ.get('PROBE_OC_HOST', 'openshift.xchem.diamond.ac.uk')
OC_USER = os.environ.get('PROBE_OC_USER', 'admin')

# SMTP (Mailgun) details...
MAILGUN_ADDR = 'smtp.mailgun.org'
MAILGUN_PORT = 587

# The email address of the Security Probe.
# The email 'from' value.
PROBE_EMAIL = 'Security Probe <dls.security.probe@informaticsmatters.com>'

# The period of time to pause
# prior to entering the probe loop
PRE_PROBE_DELAY_S = 10.0

# Timeout of the probe call
PROBE_TIMEOUT_S = 3.0

# The time (in seconds) to wait after suspending the
# service to wait for a loss of response.
POST_TERMINATE_PERIOD_S = 120
# The polling period during this phase.
POST_TERMINATE_PROBE_PERIOD_S = 5

# Probe status, returned by probe().
# It's either safe, at risk or there were problems probing.
class ProbeResult(Enum):
    SAFE = 1
    AT_RISK = 2
    ERROR = 3


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


def sendmail(msg):
    """Sends the MIMETest message to the mailgun account.

    :param msg: The message to send
    :type msg: ``MIMEText``
    """

    smtp = smtplib.SMTP(MAILGUN_ADDR, MAILGUN_PORT)
    rv = smtp.login(MAILGUN_LOGIN, MAILGUN_PASSWORD)
    if rv[0] == 235:
        smtp.sendmail(PROBE_EMAIL,
                      RECIPIENTS.split(','),
                      msg.as_string())
    smtp.quit()


def email_warning():
    """Sends an email, driven by the first probe failure.

    This email delivers a warning that the first probe attempt has
    failed. Another email will come when the probe fails a second time.
    """
    # Do nothing if no recipients
    if not RECIPIENTS:
        warning('Skipping warning email (no recipients)')
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

    sendmail(msg)

    message('Sent warning email')


def email_recovery():
    """Sends an email, driven a recovery from an initial failure.

    This email delivers a message saying that the previous warning
    has now cleared. At this point the error failure count will have
    been reset.
    """
    # Do nothing if no recipients
    if not RECIPIENTS:
        warning('Skipping recovery email (no recipients)')
        return

    msg = MIMEText("The Fragalysis %s Project's Security Probe"
                   " has recovered from its initial failure.\n\n"
                   "The Security Probe has been reset and will run again"
                   " in %s minutes."
                   % (NAMESPACE_H, PERIOD_M),
                   _charset='utf-8')

    msg['Subject'] = 'Security Probe Recovered' \
                     ' - Fragalysis %s Project' \
                     % NAMESPACE_H
    msg['From'] = PROBE_EMAIL
    msg['To'] = RECIPIENTS

    sendmail(msg)

    message('Sent recovery email')


def email_suspension():
    """Sends an email, driven by the final probe failure.

    This email delivers a warning that the final security probe attempt has
    failed and the probed service is being shutdown.
    """
    # Do nothing if no recipients
    if not RECIPIENTS:
        warning('Skipping suspension email (no recipients)')
        return

    msg = MIMEText("The Fragalysis %s Project's Security Probe"
                   " has detected too many failures.\n\n"
                   "The service is now being suspended.\n\n"
                   "You now need to check the service implementation"
                   " and deploy a new working solution."
                   % NAMESPACE_H,
                   _charset='utf-8')

    msg['Subject'] = 'Security Probe Failure' \
                     ' - Fragalysis %s Project' \
                     ' - Service Suspended' % NAMESPACE_H
    msg['From'] = PROBE_EMAIL
    msg['To'] = RECIPIENTS

    sendmail(msg)

    message('Sent suspension email')


def email_suspension_failure():
    """Sends an email, driven by the failure to suspend the service.

    This email delivers a warning that the suspension of the probed
    service failed and there is a possibility that it is still running
    and vulnerable.
    """
    # Do nothing if no recipients
    if not RECIPIENTS:
        warning('Skipping suspension failure email (no recipients)')
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

    sendmail(msg)

    message('Sent suspension failure email')


def probe():
    """Probes the service, returning one of SAFE, AT_RISK or ERROR
    if the response was OK, not OK or there were problems getting a response.

    :return: The probe result
    :rtype; ``ProbeResult``
    """
    # Probe the location (REST GET)
    # with a 4-second timeout
    resp = None
    try:
        resp = requests.get(LOCATION,
                            headers={'accept': 'application/json'},
                            timeout=PROBE_TIMEOUT_S)
    except:
        # Any failure will be logged
        # but ignored.
        pass

    # Assume an error
    # (could not get a response)
    ret_val = ProbeResult.ERROR
    if resp and resp.status_code == 200:

        # If successful, check the content.
        # the 'count' must be '0'
        if 'count' in resp.json():
            # It's either going to be SAFE or AT_RISK...
            count = resp.json()['count']
            if count:
                ret_val = ProbeResult.AT_RISK
                warning('At risk - probe "count" value of %d' % count)
            else:
                ret_val = ProbeResult.SAFE
        else:
            # Count not in the response. Odd?
            warning('"count" not in the response')

    else:
        # No response or not 200
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
    error('The location is not defined')
# A deployment (behind the service we're monitoring) must be provided.
if not DEPLOYMENT:
    error('The deployment is not defined')
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
    error('The period is not a number (%s)' % PERIOD_M)
# Threshold must be a number
try:
    threshold_int = int(THRESHOLD)
except ValueError:
    error('The threshold is not a number (%s)' % THRESHOLD)
# And greater than 1
if threshold_int < 2:
    error('The threshold must be 2 or more')

# Ready to go...
#
# Log startup conditions, pause for a moment
# then enter the probe/sleep loop

# Normalise the list of email addresses.
# Split and join with a comma
if RECIPIENTS:
    RECIPIENTS = ','.join(RECIPIENTS.split())

message('LOCATION="%s"' % LOCATION)
message('RECIPIENTS="%s"' % RECIPIENTS)
message('PERIOD_M=%s' % PERIOD_M)
message('THRESHOLD=%s' % THRESHOLD)

message('In pre-probe delay...')
time.sleep(PRE_PROBE_DELAY_S)

message('Probing...')

failure_count = 0
time_to_suspend = False
while not time_to_suspend:

    # Probe
    # If success then reset any accumulated failure
    probe_result = probe()
    if probe_result == ProbeResult.AT_RISK:

        failure_count += 1
        message('Service at risk (%d/%d)'
                % (failure_count, threshold_int))
        if failure_count == 1:
            email_warning()

    elif probe_result == ProbeResult.SAFE:

        if failure_count:
            failure_count = 0
            message('Service is safe (reset)')
            email_recovery()

    elif probe_result == ProbeResult.ERROR:

        # An error after a failure
        # is considered an additional failure
        if failure_count:
            failure_count += 1
            message('Probe error during failure (%d/%d)'
                    % (failure_count, threshold_int))

    # Have we seen sufficient failures
    # to warrant suspending the service?
    if failure_count >= threshold_int:
        message('Reached at-risk threshold')
        time_to_suspend = True

    # If not failed,
    # sleep prior to the next attempt...
    if not time_to_suspend:
        time.sleep(period_s_int)

# If we get here the probe has failed!
# We must send an email.

message('Suspending the service...')

# Suspend the service.
# To suspend the service we scale the DeploymentConfig
# so that the number of replicas is 0...
suspended = False

# Login
#
message('Logging in to OpenShift...')
cmd = 'oc login %s -u %s -p %s' % (OC_HOST, OC_USER, OC_PASSWORD)
result = subprocess.run(cmd.split(),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
if result.returncode:
    # Login failed!
    message('Login failed! (%d)' % result.returncode)
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
        message('Project failed! (%d)' % result.returncode)
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
            message('Suspension failed! (%d)' % result.returncode)
        else:
            message('Suspended')
            email_suspension()

            # Continue to probe until not failed
            #
            message('Waiting for service termination...')
            waited_s = 0
            waited_long_enough = False
            while not waited_long_enough:
                if probe() != ProbeResult.AT_RISK:
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
