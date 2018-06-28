#!/usr/bin/env python

"""A simple module to recover a backup.

Expects Python 3 (recursive glob).

The backup directory (BACKUP_DIR) is expected to have
been mounted as some form of volume in the container image.

A number of environment variables control this utility: -

-   FROM_BACKUP         The timestamp. This can be the ISO-8601 portion of
                        the original backup filename, 'NONE' or 'LATEST'.
                        The provided string is converted to upper-case.
                        If 'NONE' the recover module simply displays
                        all the backups on the backup volume.
                        If 'LATEST' then the latest backup file on the volume
                        is used to recover the database from. If
                        a time the file whose name matches the provided time
                        will be used as a source of the recovery.
                        (default 'NONE')

-   PGHOST              The Postgres database Hostname.
                        (default 'postgres')

-   PGUSER              The Postgres database User.
                        (default 'postgres')

Alan Christie
Informatics Matters
June 2018
"""

import datetime
import glob
import os
import sys
import subprocess

# The module version.
# Please adjust on every change
# following Semantic Versioning principles.
__version__ = '1.0.0'

# Alternatives for Backup
B_NONE = 'NONE'
B_LATEST = 'LATEST'

# Expose our version...
print('# recovery.__version__ = %s' % __version__)

# The backup time (NONE by default).
# This is the time from the backup filename,
# i.e. '2018-06-25T21:05:07Z'
FROM_BACKUP = os.environ.get('FROM_BACKUP', 'LATEST').upper()
# Extract configuration from the environment.
PGHOST = os.environ.get('PGHOST', 'postgres')
PGUSER = os.environ.get('PGUSER', 'postgres')

# The backup config.
# The root dir, below which you're likely to find
# hourly, daily, weekly and monthly backup directories.
BACKUP_ROOT_DIR = '/backup'
BACKUP_FILE_PREFIX = 'backup'

# Echo configuration...
print('# FROM_BACKUP = %s' % FROM_BACKUP)
print('# PGHOST = %s' % PGHOST)
print('# PGUSER = %s' % PGUSER)

# Recover...
#
# 1. Check that the root backup directory exists
# 2. Display all backups
# 3. If BACKUP_FROM is 'NONE'
#       Leave
# 4.  If BACKUP_FROM is 'LATEST'
#       use the most recent backup
#    Else recover the named backup from a file whose name
#       matches the provided string, normally an ISO8601 datetime string.
#        a date and time (i.e. '2018-06-25T21:05:07Z')

RECOVERY_START_TIME = datetime.now()
print('--] Hello [%s]' % RECOVERY_START_TIME)
#####
# 1 #
#####
if not os.path.isdir(BACKUP_ROOT_DIR):
    print('--] Backup root directory does not exist (%s). Leaving.' % BACKUP_ROOT_DIR)
    sys.exit(3)

#####
# 2 #
#####
# A dictionary of backup files and their directories.
LATEST_BACKUP = None
KNOWN_BACKUPS = {}
FILE_SEARCH = os.path.join(BACKUP_ROOT_DIR, '**', BACKUP_FILE_PREFIX + '*')
BACKUPS = glob.glob(FILE_SEARCH)
for BACKUP in BACKUPS:
    FILENAME = os.path.basename(BACKUP)
    DIRECTORY = os.path.dirname(BACKUP)
    if FILENAME not in KNOWN_BACKUPS:
        KNOWN_BACKUPS[FILENAME] = DIRECTORY
print('--] Known backups...')
if KNOWN_BACKUPS:
    for KNOWN_BACKUP in sorted(KNOWN_BACKUPS):
        print('    %s' % KNOWN_BACKUP)
else:
    print('    None')

#####
# 3 #
#####
if FROM_BACKUP in [B_NONE]:
    print('--] Backup from is NONE. Nothing to do')
    sys.exit(0)

#####
# 4 #
#####
if not LATEST_BACKUP:
    print('--] Asked to recover LATEST but there are no backups. Sorry.')
    sys.exit(0)

BACKUP_FILE = None
if FROM_BACKUP in [B_LATEST]:
    print('--] Attempting to recover from LATEST backup')
    BACKUP_FILE = os.path.join(KNOWN_BACKUPS[LATEST_BACKUP], LATEST_BACKUP)
else:
    print('--] Attempting to recover from %s backup' % FROM_BACKUP)
    # Search the known back keys.
    for KNOWN_BACKUP in KNOWN_BACKUPS:
        if FROM_BACKUP in KNOWN_BACKUP:
            BACKUP_FILE = os.path.join(KNOWN_BACKUPS[KNOWN_BACKUP], KNOWN_BACKUP)
            break
if not BACKUP_FILE:
    print('--] Could not find the backup. Leaving.')
    sys.exit(0)

print('--] Recovering from %s' % BACKUP_FILE)
print('--] Done')
