#!/usr/bin/env python

# pylint: disable=invalid-name

"""get_unbuilt_data_directory.py

Prints the relative source data directory name if the most recent
data directory does not appear to be in the latest corresponding
Docker image. As this utility is used to build more than one type of
image (i.e. graph and web) the precise behaviour is controlled by a number
of environment variables (described below).

Optional environment variables: -

-   SOURCE_DATA_ROOT The root directory for source data
                     Default: /fragalysis/graph_data

-   TARGET_IMAGE     The name of the image to build
                     Default: fragalysis-cicd/graph-stream

-   FORCE_BUILD      Set to 'Yes' to always build a new image
                     Default: No

-   HOURLY_DATA      Set to Yes of the source data is expected to change
                     hourly. Data that changes hourly must use directory
                     names of the format YYYY-MM-DDTHH, i.e.
                     2018-01-02T10 for data available at 10AM
                     on the 2nd January 2018. If not set the data is expected
                     to change daily, using directory names of the format
                     YYYY-MM-DD.
                     Source data is expected in subdirectories of the
                     SOURCE_DATA_ROOT.
                     Default: No

-   INSIST_ON_READY  Set to 'Yes' to avoid building a directory of data
                     unless the file 'READY' is present in the source
                     directory.
                     Default: No

-   READY_FILE       Provides the name of the _ready_ file.
                     Default: READY

At the time of writing the Agent used in Jenkins has Python 2.7.5
installed so this is a Python 2.7-compliant module.
"""

from __future__ import print_function

import logging
from logging.config import dictConfig
import json
import os
import re
import subprocess
import sys
import yaml

# Extract environment variable values (with defaults)
SOURCE_DATA_ROOT = os.environ.get('SOURCE_DATA_ROOT', '/fragalysis/graph_data')
TARGET_IMAGE = os.environ.get('TARGET_IMAGE', 'fragalysis-cicd/graph-stream')

FORCE_BUILD = os.environ.get('FORCE_BUILD', 'No').lower() in ['y', 'yes']
HOURLY_DATA = os.environ.get('HOURLY_DATA', 'No').lower() in ['y', 'yes']
INSIST_ON_READY = os.environ.get('INSIST_ON_READY', 'No').lower() in ['y', 'yes']
READY_FILE = os.environ.get('READY_FILE', 'READY')

REGISTRY_USER = os.environ.get('REGISTRY_USER', 'jenkins')
REGISTRY_USER_TOKEN = os.environ.get('REGISTRY_USER_TOKEN', 'jenkins123')

# The image we'll be manufacturing...
REGISTRY = 'docker-registry.default.svc:5000'
TAG = 'latest'

# The key of the label value used to record
# the source data the image was built with.
# If the image was build from data from '2018-01-01'
# one of its 'Labels' will be 'data.origin':'2018-01-01'
DATA_ORIGIN_KEY = 'data.origin'

# Regular expression for each source data directory.
# These exist in the SOURCE_DATA_ROOT.
DATA_DIR_RE = r'\d\d\d\d-\d\d-\d\d'
if HOURLY_DATA:
    DATA_DIR_RE += r'T\d\d$'
else:
    DATA_DIR_RE += '$'

# -----------------------------------------------------------------------------

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

# -----------------------------------------------------------------------------

LOGGER.info('SOURCE_DATA_ROOT="%s"', SOURCE_DATA_ROOT)
LOGGER.info('TARGET_IMAGE="%s"', TARGET_IMAGE)
LOGGER.info('FORCE_BUILD=%s', FORCE_BUILD)
LOGGER.info('HOURLY_DATA=%s', HOURLY_DATA)
LOGGER.info('INSIST_ON_READY=%s', INSIST_ON_READY)
LOGGER.info('READY_FILE=%s', READY_FILE)
LOGGER.info('REGISTRY_USER=%s', REGISTRY_USER)

# Does the root data directory exist?
# If it does not maybe the Agent volume mounts are missing - so it's bad!
if not os.path.isdir(SOURCE_DATA_ROOT):
    LOGGER.error('The data root directory does not exist.'
                 ' Is anything mounted at %s?', SOURCE_DATA_ROOT)
    sys.exit(0)

# Get the content of the root data directory.
most_recent_data_dir = None
DATA_DIRS = sorted(os.listdir(SOURCE_DATA_ROOT))
if not DATA_DIRS:
    # No data directories.
    LOGGER.error('No data directories in the root (%s)', SOURCE_DATA_ROOT)
    sys.exit(0)

# We'll assume the last one holds the most recent data
# but if INSIST_ON_READY is set we search backwards for the most
# recent directory that is READY. In our search we omit poorly
# formatted directories, and anything that's not a directory.
#
# There may not be any data directories and there may be none
# that are READY.
if INSIST_ON_READY:
    # Walk back through the data directories
    # until we find one that is READY
    LOGGER.info('Searching for READY data...')
    for data_dir in reversed(DATA_DIRS):
        data_path = os.path.join(SOURCE_DATA_ROOT, data_dir)
        if os.path.isdir(data_path):
            if re.match(DATA_DIR_RE, data_dir):
                if os.path.exists(os.path.join(data_path, READY_FILE)):
                    LOGGER.info('DataDir: %s is READY', data_dir)
                    most_recent_data_dir = data_dir
                    break
                else:
                    LOGGER.warning('DataDir: %s is not READY', data_dir)
            else:
                LOGGER.warning('DataDir: %s uses an incorrect format', data_dir)
        else:
            LOGGER.warning('DataDir: %s is not a directory', data_dir)
else:
    # Not insisting on READY,
    # just pick the most recent directory...
    most_recent_data_dir = DATA_DIRS[-1]

# Did we find a data directory?
if not most_recent_data_dir:
    # No data directories.
    LOGGER.error('Could not find a viable data directory')
    LOGGER.info('Looked at...')
    for data_dir in DATA_DIRS:
        LOGGER.info('+ %s', data_dir)
    sys.exit(0)

# Is the directory name correct?
if not re.match(DATA_DIR_RE, most_recent_data_dir):
    # Doesn't look right
    LOGGER.error('Most recent data directory name'
                 ' is not correct (%s)', most_recent_data_dir)
    sys.exit(0)
most_recent_data_path = os.path.join(SOURCE_DATA_ROOT, most_recent_data_dir)
if not os.path.isdir(most_recent_data_path):
    # Most recent does not look like a directory.
    LOGGER.error('Most recent data directory is not a directory'
                 ' (%s)', most_recent_data_dir)
    sys.exit(0)

# OK - fit to continue if we get here...

# We have source data (that is READY) if we get here!
# Next stage build if the latest image does not contain this data
# (or build regardless if FORCE_BUILD is set).

if FORCE_BUILD:

    LOGGER.warning('Forcing build (image inspection will not take place)')

else:

    # Inspect the current image content and obtain the Labels.
    # One label will be the source data directory used to build the image
    # with the key DATA_ORIGIN_KEY and a value that is the directory
    # that housed the original data.
    #
    # We may not have an image, it may not have labels
    # or the label may be for an older data directory.
    # We need to build a new image for all these conditions.
    image_spec = '%s/%s:%s' % (REGISTRY, TARGET_IMAGE, TAG)
    cmd = 'skopeo inspect --tls-verify=false'
    cmd += ' --creds=%s:%s docker://%s' % (REGISTRY_USER,
                                           REGISTRY_USER_TOKEN,
                                           image_spec)
    image_str_info = None
    image_data_origin = None
    # Protect from failure...
    # pylint: disable=bare-except
    try:
        image_str_info = subprocess.check_output(cmd.split())
    except:
        LOGGER.warning('Failed inspecting the image (%s)', image_spec)
    if image_str_info:
        image_json_info = json.loads(image_str_info)
        # If there are some labels
        # does one look like a data source label?
        # Labels should appear as a dictionary.
        labels = image_json_info['Labels']
        if labels and DATA_ORIGIN_KEY in labels:
            image_data_origin = labels[DATA_ORIGIN_KEY]
        else:
            LOGGER.warning('Image has no "%s" label', DATA_ORIGIN_KEY)

    # If the current label matches the most recent data directory
    # then there's nothing to do -
    # the latest image is build from the latest data directory.
    if image_str_info and image_data_origin == most_recent_data_dir:
        LOGGER.info('The latest image is already built from'
                    ' the most recent data ("%s")', image_data_origin)
        sys.exit(0)
    elif image_str_info:
        LOGGER.info('Latest image (%s) is built from "%s", not "%s"',
                    image_spec, image_data_origin, most_recent_data_dir)
    else:
        LOGGER.info('There does not appear to be a latest image')


# There is no image, or its label does not match the
# most recent data directory and so we print the
# data directory, which can be used to trigger a build...
LOGGER.info('A new image needs building for "%s"', most_recent_data_dir)
print(most_recent_data_dir)
