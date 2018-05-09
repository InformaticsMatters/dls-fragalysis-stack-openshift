#!/usr/bin/env python

"""get_unbuilt_data_directory.py

Prints the relative source data directory name if the most recent
data directory does not appear to be in the latest corresponding
Docker image.

Environment control the operation of this module: -

-   SOURCE_DATA_ROOT The root directory for source data
-   GRAPH_IMAGE      The name of the graph image
-   GRAPH_TAG        The name of the image tag to inspect

Source data is expected in subdirectories of the SOURCE_DATA_ROOT
and the data is assumed to be 'ready for consumption' if the
file  'READY' exists in the dub-directory.

At the time of writing the Agent used in Jenkins has Python 2.7.5
installed so this is a Python 2.7-compliant module.
"""

from __future__ import print_function

import json
import os
import re
import subprocess
import sys

# Extract environment variable values (with defaults)
SOURCE_DATA_ROOT = os.environ.get('SOURCE_DATA_ROOT', '/source-data')
FORCE_BUILD = os.environ.get('FORCE_BUILD', 'No')

# The image we'll be manufacturing...
REGISTRY  = 'docker-registry.default:5000'
IMAGE = 'fragalysis-cicd/graph-stream'
TAG = 'latest'

# The Registry
# The key of the label value used to record
# the source data the image was built with.
# If the image was build from data from '2018-01-01'
# one of its 'Labels' will be 'data.origin':'2018-01-01'
DATA_ORIGIN_KEY = 'data.origin'

# Regular expression for each source data directory.
# These exist in the SOURCE_DATA_ROOT.
DATA_DIR_RE = '\d\d\d\d-\d\d-\d\d'

# Does the root data directory exist?
if not os.path.isdir(SOURCE_DATA_ROOT):
    sys.exit(0)

# Search the root data directory for sub-directories.
# We'll assume the last one holds the most recent data.
# There may not be any data directories.
most_recent_data_dir = None
DATA_DIRS = sorted(os.listdir(SOURCE_DATA_ROOT))
if DATA_DIRS:
    most_recent_data_dir = DATA_DIRS[-1]
else:
    # No data directories.
    sys.exit(0)
# Is the directory name correct?
if not re.match(DATA_DIR_RE, most_recent_data_dir):
    # Doesn't look right
    sys.exit(0)
most_recent_data_path = os.path.join(SOURCE_DATA_ROOT, most_recent_data_dir)
if not os.path.isdir(most_recent_data_path):
    # Most recent does not look like a directory.
    sys.exit(0)
# Check data is READY
if not os.path.exists(os.path.join(most_recent_data_path, 'READY')):
    # Directory exists but it's not ready.
    sys.exit(0)

# We have source data (that is READY) if we get here!

# Inspect the current image content and obtain the Labels.
# One label will be the source data directory used to build the image
# with the text 'Source=2018-01-01'.
# We may not have an image, it may not have labels
# or the label may be for an older data directory.
# We need to build a new image for all these conditions.
cmd = 'buildah inspect --type image %s/%s:%s' % (REGISTRY, IMAGE, TAG)
image_str_info = None
image_json_info = None
image_data_origin = None
# Protect from failure...
try:
    image_str_info = subprocess.check_output(cmd.split())
except:
    pass
if image_str_info:
    image_json_info = json.loads(image_str_info)
    # If there are some labels
    # does one look like a data source label?
    # Labels should appear as a dictionary.
    labels = image_json_info['OCIv1']['config']['Labels']
    if labels and DATA_ORIGIN_KEY in labels:
        image_data_origin = labels[DATA_ORIGIN_KEY]

# If the current label matches the most recent data directory
# then there's nothing to do -
# the latest image is build from the latest data directory.
if FORCE_BUILD.lower() in ['n', 'no'] and \
        image_data_origin == most_recent_data_dir:
    sys.exit(0)

# There is no image, or its label does not match the
# most recent data directory and so we print the
# data directory, which can be used to trigger a build...
print(most_recent_data_dir)
