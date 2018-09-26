#!/usr/bin/env python

"""probe.py

The probe is designed to run as an OpenShift Job and terminates
(after suspending the probed service) when the failure conditions have
been met. The Job may also terminate if there in an unrecoverable
error condition whereby it will log the condition but exit with
a code of 0 to avoid being re-spawned by OpenShift.

LOCATION    The rest location to probe.

PERIOD_M    The period between probes (minutes)
            (default 5)

THRESHOLD   The number of failures after which
            the service will be suspended.
            (default 2)

RECIPIENTS  A comma-separated list of email recipients.
            This is optional, if not provided no email will be
            sent.
DEPLOYMENT  The name f the deployment that shoul dbe scaled-down
            onm probe failure.

"""

import os
import requests
import smtplib
import sys
import subprocess
import time

LOCATION_ENV = 'PROBE_LOCATION'
LOCATION = os.environ.get(LOCATION_ENV)
PERIOD_M_ENV = 'PROBE_PERIOD_M'
PERIOD_M = os.environ.get(PERIOD_M_ENV, '5')
THRESHOLD_ENV = 'PROBE_THRESHOLD'
THRESHOLD = os.environ.get(THRESHOLD_ENV, '2')
RECIPIENTS_ENV = 'PROBE_RECIPIENTS'
RECIPIENTS = os.environ.get(RECIPIENTS_ENV)
DEPLOYMENT_ENV = 'PROBE_DEPLOYMENT'
DEPLOYMENT = os.environ.get(DEPLOYMENT_ENV)
NAMESPACE_ENV = 'PROBE_DEPLOYMENT'
NAMESPACE = os.environ.get(NAMESPACE_ENV)

OC_HOST = os.environ.get('PROBE_OC_HOST')
OC_USER = os.environ.get('PROBE_OC_USER')
OC_PASS = os.environ.get('PROBE_OC_PASS')

# The period of time to pause, once we're initialised,
# prior to entering the probe loop
PRE_PROBE_DELAY_S = 2.0

def error(msg):
    """Prints the supplied error message and exists (cleanly).

    :param msg: A short error message
    :type msg: ``String``
    """
    print('ERROR: %s' % msg)
    sys.exit(0)


def email_warning():
    """Sends a warning email"""
    print('-) Sent warning email')
    pass


def email_suspension():
    """Sends a service suspension email"""
    print('-) Sent suspension email')
    pass


def email_suspension_failure():
    """Sends a fail to suspend service email"""
    print('-) Sent suspension failure email')
    pass


# Pre-flight checks...

# Must have OC host, user and password
if not OC_HOST:
    error('An OC host must be supplied')
if not OC_USER:
    error('An OC user must be supplied')
if not OC_PASS:
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
# Pause for a moment
# then enter the probe/sleep loop

print('-) LOCATION="%s"' % LOCATION)
print('-) PERIOD_M=%s' % PERIOD_M)
print('-) THRESHOLD=%s' % THRESHOLD)

print('-) Pre-probe delay (%s)...' % PRE_PROBE_DELAY_S)
time.sleep(PRE_PROBE_DELAY_S)

print('-) Probing until failure...')
location_headers = {'accept': 'application/json'}
failure_count = 0
failed = False
while not failed:

    # Probe the location (REST GET)
    # with a 4-second timeout
    try:
        resp = requests.get(LOCATION,
                            headers=location_headers,
                            timeout=4)
    except:
        # Any failure will be logged
        # but ignored.
        pass

    # If successful, check the content.
    # the 'count' must be '0'
    if resp and resp.status_code == 200:
        if 'count' in resp.json():
            count = resp.json()['count']
            if count:
                failure_count += 1
                print('-) Ooops - count is %s.'
                      ' Probe failed (%d/%d).' % (count,
                                                  failure_count,
                                                  threshold_int))
                if failure_count == 0:
                    email_warning()
                elif failure_count >= threshold_int:
                    print('-) Reached failure threshold')
                    failed = True
        else:
            # Count not in the response. Odd?
            print('-) WARNING: "count" not in the response')
    else:
        if resp:
            print('-) WARNING: Got status %d' % resp.status_code)
        else:
            print('-) WARNING: Got no response')

    # If not failed, sleep prior to the next probe...
    if not failed:
        time.sleep(period_s_int)

# If we get here the probe has failed!
# We must send a new email and suspend the service.

print('-) Probe failure - suspending the service...')

email_suspension()

# To suspend the service we scale the DeploymentConfig
# so that the number of replicas is 0...

# Login
#
cmd = 'oc login %s -u %s -p %s' % (OC_HOST, OC_USER, OC_PASS)
result = subprocess.run(cmd.split())
if result.returncode:
    # Login failed!
    print('-) Login failed!')
    pass
print('-) Logged in!')

# Project
#
cmd = 'oc project %s' % NAMESPACE
result = subprocess.run(cmd.split())
if result.returncode:
    # Login failed!
    print('-) Project failed!')
    pass
print('-) Moved project!')

# Scale
#
#cmd = 'oc scale dc %s --replicas=0' % DEPLOYMENT
cmd = 'oc get projects'
result = subprocess.run(cmd.split())
if result.returncode:
    # The scaling command failed!
    pass
print('-) Suspended!')

print('-) Service Suspended. See you on the other side...')

# We leave without an error.
# The Job will terminate until we're run again.
