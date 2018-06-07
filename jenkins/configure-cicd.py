#!/usr/bin/env python

"""A Python (3.5) module to automate the configuration and backup of the
Fragalysis CI/CD deployment. We can get (for archioving) and create jobs
(from an archive)

The following environment variables are required: -

    FRAG_CICD_USER  The Jenkins username
    FRAG_CICD_TOKEN The Jenkins user API token

>   Your user ID and API token can be obtained from your Jenkins login.
    Click your name (upper-right corner), click Configure (left-side menu)
    and then click 'Show API Token'.

If SSL certificates are not properly installed you may need to defeat the
built-in SSL validation that takes place. You can do this with the following
environment variable: -

    export PYTHONHTTPSVERIFY=0
"""

import argparse
import os
import glob
import logging
from logging.config import dictConfig
import sys
import yaml
import jenkins

J_USER = os.environ['FRAG_CICD_USER']
J_TOKEN = os.environ['FRAG_CICD_TOKEN']

# URLs for the test and production servers.
SERVERS = {'test': 'jenkins-fragalysis-cicd.apps.xchem.diamond.ac.uk',
           'prod': 'jenkins-fragalysis-cicd-prod.apps.xchem.diamond.ac.uk'}
# Our job configuration directory
JOB_DIR = 'jobs'
#  A list of recognised views...
VIEW_NAMES = ['Fragalysis (Master)']

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

# pylint: disable=too-few-public-methods
class JenkinsServer:
    """Class providing Jenkins configuration services.
    """

    def __init__(self, url):
        """Initialise the Jenkins server. URL and credentials are expected
        to be defined in global variables.

        :param url: The server URL
        :type url: ``String``
        """

        # Connect (and then try and get the server version)...
        LOGGER.info('Connecting to Jenkins...')
        self.server = None
        self.server_version = None
        try:
            self.server = jenkins.Jenkins(url)
        except BaseException as error:
            LOGGER.error('Failed to connect (exception follows)')
            LOGGER.info(error)

        if self.server:
            try:
                self.server_version = self.server.get_version()
            except BaseException as error:
                LOGGER.error('Failed to get server version (exception follows)')
                LOGGER.info(error)
            if self.server_version:
                LOGGER.info('Connected (Jenkins v%s)', self.server_version)

    def get_jobs(self):
        """Gets all the job configurations from the 'known' views.

        :return: Number of jobs retrieved
        :rtype: ``int``
        """
        # Do nothing if we do not appear to be connected.
        if not self.server_version:
            return 0

        LOGGER.info('Getting job configurations...')

        num_got = 0
        for view_name in VIEW_NAMES:
            jobs = self.server.get_jobs(view_name=view_name)
            for job in jobs:
                job_name = job['name']
                LOGGER.info('Getting "%s" from "%s" view...', job_name, view_name)
                job_config = self.server.get_job_config(job_name)
                job_config_filename = os.path.join(JOB_DIR, job_name + '.xml')
                job_file = open(job_config_filename, 'w')
                job_file.write(job_config)
                job_file.close()
                num_got += 1

        LOGGER.info('Got (%s)', num_got)

        return num_got

    def set_jobs(self, force=False):
        """Sets up the fragalysis CI/CD Jobs.

        :param force: True to force the action
        :type force: ``Boolean``
        :return: True on success
        :rtype: ``Boolean``
        """
        # Do nothing if we do not appear to be connected.
        if not self.server_version:
            return False

        LOGGER.info('Setting job configurations...')

        # Iterate through all the jobs...
        num_set = 0
        job_files = glob.glob('jobs/*.xml')
        for job_file in job_files:
            # The name of the job is the basename of the file.
            # and we simply load the file contents (into a string)
            # to create the job (if the job does not exist)
            job_name = os.path.basename(job_file)[:-4]
            if self.server.job_exists(job_name) and not force:
                LOGGER.info('Skipping "%s" (Already Present)', job_name)
            else:
                LOGGER.info('Creating "%s"...', job_name)
                job_definition = open(job_file, 'r').read()
#                self.server.create_job(job_name, job_definition)
                num_set += 1

        LOGGER.info('Set (%s)', num_set)

        # Success if we get here...
        return True


if __name__ == '__main__':

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

    # Lookup the server URL and then connect and perform the action...
    J_URL = SERVERS[ARGS.server]
    J_URL = 'https://%s:%s@%s' % (J_USER, J_TOKEN, J_URL)
    JS = JenkinsServer(J_URL)
    if ARGS.action == 'get':
        JS.get_jobs()
    elif ARGS.action == 'set':
        JS.set_jobs(force= ARGS.force)
