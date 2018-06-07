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

import os
import logging
from logging.config import dictConfig
import sys
import yaml
import jenkins

J_USER = os.environ['FRAG_CICD_USER']
J_TOKEN = os.environ['FRAG_CICD_TOKEN']
J_DOMAIN = 'apps.xchem.diamond.ac.uk'
J_SERVICE = 'jenkins-fragalysis-cicd'
J_URL = 'https://%s:%s@%s.%s' % (J_USER, J_TOKEN, J_SERVICE, J_DOMAIN)

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

    def __init__(self):
        """Initialise the Jenkins server. URL and credentials are expected
        to be defined in global variables.
        """

        # Connect (and then try and get the server version)...
        LOGGER.info('Connecting to Jenkins...')
        self.server = None
        self.server_version = None
        try:
            self.server = jenkins.Jenkins(J_URL)
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
        """Gets all the jobs configurations from the 'known' views.
        """
        LOGGER.info('Getting job configurations...')
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
        LOGGER.info('Done.')


if __name__ == '__main__':

    JS = JenkinsServer()
    JS.get_jobs()
