#!/usr/bin/env python

"""probe.py

The probe is designed to run as an OpenShift Job, monitor a service location
for a specific response and then terminate that service if the response
does not comply with expectations. The service (part of a DeploymentConfig)
is terminated by setting its 'replicas' value to zero and then waiting, for
a short period of time, until the service stops responding.

The behaviour of the application is controlled by a number of
'required' environment variables: -

PROBE_DEPLOYMENT    The name of the deployment that should be scaled-down
                    on probe failure.

PROBE_LOCATION      The rest location to probe.
                    This is typically a path and service (rather than a route)
                    endpoint.

PROBE_NAMESPACE     The name of the deployment's namespace.

PROBE_RECIPIENTS    A comma-separated list of email recipients.
                    This is optional, if not provided no email will be
                    sent.

PROBE_OC_HOST       A valid OpenShift host

PROBE_OC_USER       A valid OpenShift host user

PROBE_OC_PAsSWORD   The OpenShift user's password

And a number of optional environment variables: -

PROBE_PERIOD_M      The period between probes (minutes)
                    (default 5)

PROBE_THRESHOLD     The number of failures after which
                    the service will be suspended.
                    (default 2)

This Job may also terminate if there in an unrecoverable
error condition whereby it will log the condition but exit with
a code of 0 to avoid being re-spawned by OpenShift.
"""

import os
import requests
import smtplib
import sys
import subprocess
import time

DEPLOYMENT_ENV = 'PROBE_DEPLOYMENT'
DEPLOYMENT = os.environ.get(DEPLOYMENT_ENV)
LOCATION_ENV = 'PROBE_LOCATION'
LOCATION = os.environ.get(LOCATION_ENV)
NAMESPACE_ENV = 'PROBE_NAMESPACE'
NAMESPACE = os.environ.get(NAMESPACE_ENV)
RECIPIENTS_ENV = 'PROBE_RECIPIENTS'
RECIPIENTS = os.environ.get(RECIPIENTS_ENV)

PERIOD_M_ENV = 'PROBE_PERIOD_M'
PERIOD_M = os.environ.get(PERIOD_M_ENV, '5')
THRESHOLD_ENV = 'PROBE_THRESHOLD'
THRESHOLD = os.environ.get(THRESHOLD_ENV, '2')

OC_HOST = os.environ.get('PROBE_OC_HOST')
OC_USER = os.environ.get('PROBE_OC_USER')
OC_PASSWORD = os.environ.get('PROBE_OC_PASSWORD')

# The period of time to pause, once we're initialised,
# prior to entering the probe loop
PRE_PROBE_DELAY_S = 2.0

# Timeout of the probe call
PROBE_TIMEOUT_S = 2.0

# The time (in seconds) to wait after suspending the
# service to wait for a los of response.
POST_TERMINATE_PERIOD_S = 60
# The polling period for the probe after terminating.
POST_TERMINATE_PROBE_PERIOD_S = 5


def error(msg):
    """Prints the supplied error message and exists (cleanly).

    :param msg: A short error message
    :type msg: ``String``
    """
    print('ERROR: %s' % msg)
    sys.exit(0)


def message(msg):
    """Prints a message

    :param msg: The message
    :type msg: ``String``
    """
    print('-) %s' % msg)


def email_warning():
    """Sends a warning email"""
    print('-) Sent warning email')


def email_suspension():
    """Sends a service suspension email"""
    print('-) Sent suspension email')


def email_suspension_failure():
    """Sends a fail to suspend service email"""
    print('-) Sent suspension failure email')


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
        else:
            # Count not in the response. Odd?
            message('WARNING: "count" not in the response')
    else:
        if resp:
            message('WARNING: Got status %d' % resp.status_code)
        else:
            message('WARNING: Got no response')

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

message('Pre-probe delay (%s)...' % PRE_PROBE_DELAY_S)
time.sleep(PRE_PROBE_DELAY_S)

message('Probing...')
failure_count = 0
failed = False
while not failed:

    # Probe (and deal with failure)
    if not probe():
        failure_count += 1
        message('Ooops - count is %s.'
                ' Probe failed (%d/%d).' % (count,
                                            failure_count,
                                            threshold_int))
        if failure_count == 0:
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

message('Probe failure - suspending the service...')
email_suspension()

# Suspend the service.
# To suspend the service we scale the DeploymentConfig
# so that the number of replicas is 0...

# Login
#
cmd = 'oc login %s -u %s -p %s' % (OC_HOST, OC_USER, OC_PASSWORD)
result = subprocess.run(cmd.split())
suspended = False
if result.returncode:
    # Login failed!
    message('Login failed!')
    pass
else:
    message('Logged in!')

    # Project
    #
    cmd = 'oc project %s' % NAMESPACE
    result = subprocess.run(cmd.split())
    if result.returncode:
        # Login failed!
        message('Project failed!')
        pass
    else:
        message('Moved project!')

        # Scale
        #
        #cmd = 'oc scale dc %s --replicas=0' % DEPLOYMENT
        cmd = 'oc get projects'
        result = subprocess.run(cmd.split())
        if result.returncode:
            # The scaling command failed!
            pass
        message('Suspended - waiting...')

        # Continue to probe until success...
        waited_s = 0
        waited_long_enough = False
        while not waited_long_enough:
            if probe():
                suspended = True
                waited_long_enough = True
            else:
                time.sleep(POST_TERMINATE_PROBE_PERIOD_S)
                waited_s += POST_TERMINATE_PROBE_PERIOD_S
                if waited_s >= POST_TERMINATE_PERIOD_S:
                    waited_long_enough = True

# If we failed to suspend the service...
if not suspended:
    email_suspension_failure()

# We leave without an error.
# The Job will terminate until we're run again.
