#!/usr/bin/env python

"""A simple module to create and manage backups.

The backup directory (BACKUP_DIR) is expected to have
been mounted as some form of volume in the container image.
"""

import glob
import os
import sys
import subprocess
import shutil
from datetime import datetime

# Extract configuration from the environment...
BACKUP_COUNT = int(os.environ.get('BACKUP_COUNT', '1'))
PGHOST = os.environ.get('PGHOST', 'localhost')

# The backup config...
BACKUP_DIR = '/backup'
BACKUP_LIVE_FILE = 'dumpall.sql'    # The new file
BACKUP_FILE_PREFIX = 'backup'       # Prefix for older files

BACKUP = os.path.join(BACKUP_DIR, BACKUP_LIVE_FILE)
BACKUP_CMD = 'touch %s' % BACKUP
#BACKUP_CMD = 'pg_dumpall --clean --file=%s' % BACKUP

# Echo configuration...
print('# PGHOST = %s' % PGHOST)
print('# BACKUP_CMD = "%s"' % BACKUP_CMD)
print('# BACKUP_COUNT = %s' % BACKUP_COUNT)

BACKUP_START_TIME = datetime.now().isoformat()
print('--] Starting backup [%s]' % BACKUP_START_TIME)

# Backup...
#
# 1. Check that the backup directory exists
# 2. If the backup file exists then do nothing
#    (the previous backup must be running)
# 3. Run the backup
# 4. Copy the live backup to a new prefixed date/time named file
#    and then remove the original file.
# 5. Remove any files that are now too old

# 1.
if not os.path.isdir(BACKUP_DIR):
    print('--] Bxkup directory does not exist (%s). Leaving.' % BACKUP_DIR)
    sys.exit(1)

# 2.
if os.path.exists(BACKUP):
    print('--] Live backup file exists (%s). Leaving.' % BACKUP)
    sys.exit(2)

# 3.
print('--] Running backup (stdout follows)...')
subprocess.run(BACKUP_CMD, shell=True)
print('--] Backup complete [%s]' % datetime.now().isoformat())

# 4.
COPY_BACKUP_FILE = '%s-%s-%s' % (BACKUP_FILE_PREFIX,
                                 BACKUP_START_TIME,
                                 BACKUP_LIVE_FILE)
print('--] Copying %s to %s...' % (BACKUP_LIVE_FILE, COPY_BACKUP_FILE))
BACKUP_TO = os.path.join(BACKUP_DIR, COPY_BACKUP_FILE)
shutil.copyfile(BACKUP, BACKUP_TO)
os.remove(BACKUP)

# 5.
FILE_SEARCH = os.path.join(BACKUP_DIR, BACKUP_FILE_PREFIX + '*')
EXISTING_BACKUPS = glob.glob(FILE_SEARCH)
NUM_TO_DELETE = len(EXISTING_BACKUPS) - BACKUP_COUNT
if NUM_TO_DELETE > 0:
    EXISTING_BACKUPS.sort()
    for EXISTING_BACKUP in EXISTING_BACKUPS[:NUM_TO_DELETE]:
        print('--] Removing old backup %s...' % EXISTING_BACKUP)
        os.remove(EXISTING_BACKUP)
else:
    print('--] No old backups to delete')

print('--] Done')
