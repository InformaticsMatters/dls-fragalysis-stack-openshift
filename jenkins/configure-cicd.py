#!/usr/bin/env python

"""A Python 3 module to automate the configuration and backup of the
Fragalysis CI/CD deployment. Remember to copy the `setenv-template'sh` script,
enter suitable values for the environment variables and `source` it.

If SSL certificates are not properly installed you may need to defeat the
built-in SSL validation that takes place. You can do this with the following
environment variable: -

    export PYTHONHTTPSVERIFY=0
"""

import argparse
import os
import logging
from logging.config import dictConfig
import sys
import yaml

from im_jenkins_server import ImJenkinsServer

# Essential environment variables...
J_USER = os.environ['FRAG_CICD_USER']
J_TOKEN = os.environ['FRAG_CICD_TOKEN']
J_DOCKER_PASS = os.environ['FRAG_DOCKER_PASSWORD']
J_SLACK_TOKEN = os.environ['FRAG_SLACK_TOKEN']

# URLs for the test and production servers.
SERVERS = {'test': 'jenkins-fragalysis-cicd.apps.xchem.diamond.ac.uk',
           'prod': 'jenkins-fragalysis-cicd-prod.apps.xchem.diamond.ac.uk'}
# Our job configuration directory
JOB_DIR = 'jobs'

# Load logger configuration (from cwd)...
# But only if the logging configuration is present!
LOGGING_CONFIG_FILE = 'logging.yml'
if os.path.isfile(LOGGING_CONFIG_FILE):
    LOGGING_CONFIG = None
    with open(LOGGING_CONFIG_FILE, 'r') as stream:
        try:
            LOGGING_CONFIG = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    dictConfig(LOGGING_CONFIG)
# Our logger...
LOGGER = logging.getLogger(os.path.basename(sys.argv[0])[:-3])

PARSER = argparse.ArgumentParser(description='Jenkins Configuration')
PARSER.add_argument('action',
                    choices=['get', 'set'],
                    help='The action to perform. This is typically one'
                         ' of "get" in order to get the configuration or'
                         ' "set" to set the job configuration for a server.')
PARSER.add_argument('server',
                    choices=['test', 'prod'],
                    help='The Jenkins server, typically one of "test" for'
                         ' the test server or "prod" for the production'
                         ' server.')
PARSER.add_argument('-f','--force',
                    action='store_true',
                    help='Force the action (useful during set).')
ARGS = PARSER.parse_args()

# Connect to the server
J_URL = SERVERS[ARGS.server]
J_URL_WITH_USER = 'https://%s:%s@%s' % (J_USER, J_TOKEN, J_URL)
JS = ImJenkinsServer(J_URL_WITH_USER)
if not JS.is_connected():
    LOGGER.error('Failed to connect to jenkins')
    sys.exit(1)

# Set or get?
if ARGS.action == 'get':

    LOGGER.info('Reading server configuration...')
    # You can't get the credentials!
    # Read Jobs into 'jobs-test' or 'jobs-prod'...
    JS.get_jobs('jobs-' + ARGS.server)

elif ARGS.action == 'set':

    # Destructive
    # Double-check with the user...
    print("WARNING: Setting the server value is destructive.")
    response = input("         If you're sure you want to continue enter 'YES': ")
    if response not in ['YES']:
        print('Phew! That was close!')
        sys.exit(0)

    LOGGER.info('Writing server configuration...')
    # Set credentials
    JS.set_secret_text('abcDockerPassword',
                       J_DOCKER_PASS,
                       "Docker Password")
    JS.set_secret_text('slackJenkinsIntegrationToken',
                       J_SLACK_TOKEN,
                       "Slack channel Jenkins Integration token")
    # Write Jobs from 'jobs-test' or 'jobs-prod'...
    JS.set_jobs('jobs-' + ARGS.server, force=ARGS.force)

LOGGER.info('Done')
