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

# URL for the CI/CD server.
SERVER = 'jenkins-fragalysis-cicd.apps.xchem.diamond.ac.uk'
# CLUSTER_URL
CLUSTER_URL = 'https://openshift.xchem.diamond.ac.uk'
# Our job configuration directory
JOB_DIR = 'jobs'

# Load logger configuration (from cwd)...
# But only if the logging configuration is present!
LOGGING_CONFIG_FILE = 'logging.yml'
if os.path.isfile(LOGGING_CONFIG_FILE):
    LOGGING_CONFIG = None
    with open(LOGGING_CONFIG_FILE, 'r') as stream:
        try:
            LOGGING_CONFIG = yaml.load(stream, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            print(exc)
    dictConfig(LOGGING_CONFIG)
# Our logger...
LOGGER = logging.getLogger(os.path.basename(sys.argv[0])[:-3])

# Check essential environment variables
J_USER = os.environ.get('FRAG_CICD_USER')
if not J_USER:
    LOGGER.error('You must define the environment variable FRAG_CICD_USER'
                 ' and set it to the name of the Jenkins user.')
    sys.exit(1)
J_TOKEN = os.environ.get('FRAG_CICD_TOKEN')
if not J_TOKEN:
    LOGGER.error('You must define the environment variable FRAG_CICD_USER'
                 ' and set it to the Jenkins PI token.')
    sys.exit(1)

PARSER = argparse.ArgumentParser(description='Jenkins Configuration')
PARSER.add_argument('action',
                    choices=['get', 'set'],
                    help='The action to perform. This is typically one'
                         ' of "get" in order to get the configuration or'
                         ' "set" to set the job configuration for a server.')
PARSER.add_argument('-f','--force',
                    action='store_true',
                    help='Force the action (useful during set).')
PARSER.add_argument('--disable-jobs',
                    action='store_true',
                    help='Disable the jobs as they are created or reconfigured'
                         ' (useful during set).')
PARSER.add_argument('--location',
                    type=str, nargs='?', default=SERVER,
                    help='The server address (without the http://).')
PARSER.add_argument('--cluster-url',
                    type=str, nargs='?', default=CLUSTER_URL,
                    help='The cluster console address.')
ARGS = PARSER.parse_args()

# Connect to the server
J_URL = ARGS.location
J_URL_WITH_USER = 'https://%s:%s@%s' % (J_USER, J_TOKEN, J_URL)
JS = ImJenkinsServer(J_URL_WITH_USER)
if not JS.is_connected():
    LOGGER.error('Failed to connect to jenkins')
    sys.exit(1)

# Set or get?
if ARGS.action == 'get':

    LOGGER.info('Reading server configuration...')
    # You can't get the credentials!
    # Read Jobs into 'jobs'...
    JS.get_jobs('jobs')
    # And views into 'views'...
    JS.get_views('views')

elif ARGS.action == 'set':

    J_DOCKER_USER = os.environ.get('FRAG_DOCKER_USER')
    if not J_DOCKER_USER:
        LOGGER.error('To set the configuration you must define'
                     ' the environment variable FRAG_DOCKER_USER')
        sys.exit(1)
    J_DOCKER_PASS = os.environ.get('FRAG_DOCKER_PASSWORD')
    if not J_DOCKER_PASS:
        LOGGER.error('To set the configuration you must define'
                     ' the environment variable FRAG_DOCKER_PASSWORD')
        sys.exit(1)
    J_SLACK_TOKEN = os.environ.get('FRAG_SLACK_TOKEN')
    if not J_SLACK_TOKEN:
        LOGGER.error('To set the configuration you must define'
                     ' the environment variable FRAG_SLACK_TOKEN')
        sys.exit(1)
    J_OC_USER = os.environ.get('FRAG_OC_USER')
    if not J_TOKEN:
        LOGGER.error('You must define the environment variable FRAG_OC_USER'
                     ' and set it to the OC command-line user.')
        sys.exit(1)
    J_OC_USER_PASSWORD = os.environ.get('FRAG_OC_USER_PASSWORD')
    if not J_TOKEN:
        LOGGER.error('You must define the environment variable FRAG_OC_USER_PASSWORD'
                     ' and set it to the OC command-line user password.')
        sys.exit(1)

    if not ARGS.force:
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
    JS.set_secret_text('abcDockerUser',
                       J_DOCKER_USER,
                       "Docker User")
    JS.set_secret_text('slackJenkinsIntegrationToken',
                       J_SLACK_TOKEN,
                       "Slack channel Jenkins Integration token")
    JS.set_secret_text('clusterUrl',
                       ARGS.cluster_url,
                       "The OC cluster URL")
    JS.set_secret_text('ocUser',
                       J_OC_USER,
                       "The OC user (for Agent-based OC commands)")
    JS.set_secret_text('ocUserPassword',
                       J_OC_USER_PASSWORD,
                       "The OC user password (for Agent-based OC commands)")
    # Write Jobs from 'jobs'...
    JS.set_jobs('jobs', set_disabled=ARGS.disable_jobs, force=ARGS.force)
    # Write Views from 'views'...
    JS.set_views('views', force=ARGS.force)

LOGGER.info('Done')
