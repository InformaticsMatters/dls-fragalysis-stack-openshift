#!/usr/bin/env python

"""A simple module to create and manage backups.

The backup directory (BACKUP_DIR) is expected to have
been mounted as some form of volume in the container image.

The backup files are named according to the following format: -

    <BACKUP_FILE_PREFIX>-<YYYY-MM-DDTHH:MM:SSZ>-<BACKUP_LIVE_FILE>.gz

For example: -

    backup-2018-06-25T21:05:07Z-dumpall.sql.gz

The time of the backup is the approximate time this utility is executed,
i.e. the start time of the backup.

A number of environment variables control this utility: -

-   BACKUP_TYPE         The type of backup. There are a number of pre-defined
                        types: - 'hourly', 'daily', 'weekly' and 'monthly'.
                        The 'hourly' is special in that it is the only backup
                        that generates new files, the other types simply
                        copy files to daily, weekly or monthly directories.
                        Backup files are written to directories that match
                        the type, i.e. /backup/daily. A description
                        of each type can be found below.

-   BACKUP_COUNT        The number of backup files to maintain for the given
                        backup type.

-   BACKUP_PRIOR_TYPE   The prior backup type (i.e. the type to copy from).
                        It can be one of 'daily', 'weekly', 'monthly'.
                        A 'weekly' BACKUP_TYPE would normally have a
                        'daily' BACKUP_PRIOR_TYPE. It is used to decide
                        where to get this backup's backup files from.

-   BACKUP_PRIOR_COUNT  For types other than 'hourly' this is the number of
                        backup files in the prior backup type that
                        represent a 'full' set. When the prior backup directory
                        contains this number of files the oldest is copied to
                        this backup directory. i.e. if this is a 'weekly'
                        backup and the prior type is 'daily' and you are
                        collecting '6' daily files a weekly file will be
                        created form the oldest daily directory when there are
                        '24' files in the hourly directory. This is designed
                        to prevent a backup form, copying a prior file until
                        there are sufficient prior files.

-   PGHOST              The Postgres database Hostname.
                        Used only for 'hourly' backup types

-   PGUSER              The Postgres database User.
                        Used only for 'hourly' backup types

There are four values for BACKUP_TYPE: -

- hourly    Typically the BACKUP_COUNT is 24.
            This type always starts by creating a new backup.
            It is the shortest backup period and writes to the 'hourly'
            directory. This backup is expected to be invoked hourly.
            BACKUP_PRIOR_COUNT is ignored.

- daily     This backup is configured to run once a day (at a time
            defined by the user). It copies the oldest backup from the
            'hourly' directory into the 'daily' directory but only when the
            hourly directory contains BACKUP_PRIOR_COUNT backup files
            (normally 24). It makes sure that no more than BACKUP_COUNT
            files exist in the daily directory.

- weekly    This backup is configured to run once a week (at a time
            defined by the user). It copies the oldest backup from the
            'daily' directory into the 'weekly' directory but only when the
            daily directory contains BACKUP_PRIOR_COUNT backup files
            (normally 7). It makes sure that no more than BACKUP_COUNT
            files exist in the weekly directory.

- monthly   This backup is configured to run once a month (at a time
            defined by the user). It copies the oldest backup from the
            'weekly' directory into the 'monthly' directory but only when the
            weekly directory contains BACKUP_PRIOR_COUNT backup files
            (normally 4). It makes sure that no more than BACKUP_COUNT
            files exist in the monthly directory.

Alan Christie
Informatics Matters
June 2018
"""

import glob
import os
import sys
import subprocess
import shutil
from datetime import datetime

# The module version.
# Please adjust on every change
# following Semantic Versioning principles.
__version__ = '2.0.3'

# Expose our version...
print('# backup.__version__ = %s' % __version__)

# Backup types...
B_HOURLY = 'hourly'
B_DAILY = 'daily'
B_WEEKLY = 'weekly'
B_MONTHLY = 'monthly'

# Extract configuration from the environment.
PGHOST = os.environ.get('PGHOST', 'postgres')
PGUSER = os.environ.get('PGUSER', 'postgres')
# The backup type is HOURLY by default.
# Hourly backups always create a new backup and limit
# the count to 24 (by default).
BACKUP_COUNT = int(os.environ.get('BACKUP_COUNT', '24'))
BACKUP_PRIOR_COUNT = int(os.environ.get('BACKUP_PRIOR_COUNT', '24'))
BACKUP_TYPE = os.environ.get('BACKUP_TYPE', B_HOURLY).lower()
BACKUP_PRIOR_TYPE = os.environ.get('BACKUP_PRIOR_TYPE', B_HOURLY).lower()

# The backup config.
# The root dir, below which you're likely to find
# hourly, daily, weekly and monthly backup directories.
BACKUP_ROOT_DIR = '/backup'
BACKUP_LIVE_FILE = 'dumpall.sql.gz' # The new file
BACKUP_FILE_PREFIX = 'backup'       # Prefix for older files

BACKUP_PRIOR_DIR = os.path.join(BACKUP_ROOT_DIR, BACKUP_PRIOR_TYPE)
BACKUP_DIR = os.path.join(BACKUP_ROOT_DIR, BACKUP_TYPE)

BACKUP = os.path.join(BACKUP_DIR, BACKUP_LIVE_FILE)
BACKUP_CMD = 'pg_dumpall --clean | gzip > %s' % BACKUP

# Echo configuration...
print('# BACKUP_TYPE = %s' % BACKUP_TYPE)
print('# BACKUP_COUNT = %s' % BACKUP_COUNT)
print('# BACKUP_DIR = %s' % BACKUP_DIR)
print('# BACKUP_PRIOR_TYPE = %s' % BACKUP_PRIOR_TYPE)
print('# BACKUP_PRIOR_COUNT = %s' % BACKUP_PRIOR_COUNT)
print('# PGHOST = %s' % PGHOST)
print('# PGUSER = %s' % PGUSER)

# Backup...
#
# 0. Check environment
# 1. Check that the root backup directory exists
#    and create a sub-directory if required
#
# For hourly backup types...
#
# 2. If the backup file exists then generate a warning
# 3. Run the backup (leaving if no backup was created)
# 4. Copy the live backup to a new prefixed date/time named file
#    and then remove the original file.
#
# For all all but hourly types...
#
# 5. Copy the oldest file from the prior backup.
#    Daily copies from Hourly, weekly copies form daily,
#    Monthly copies from weekly. This only happens if the prior count
#    is satisfied.
#
# For all backup types...
#
# 6. Limit the files in the current backup directory

#####
# 0 #
#####
# Check backup types...
if BACKUP_TYPE not in [B_HOURLY, B_DAILY, B_WEEKLY, B_MONTHLY]:
    print('--] Unexpected BACKUP_TYPE (%s)' % BACKUP_TYPE)
    sys.exit(1)
if BACKUP_PRIOR_TYPE not in [B_HOURLY, B_DAILY, B_WEEKLY]:
    print('--] Unexpected BACKUP_PRIOR_TYPE (%s)' % BACKUP_PRIOR_TYPE)
    sys.exit(2)

#####
# 1 #
#####
if not os.path.isdir(BACKUP_ROOT_DIR):
    print('--] Backup root directory does not exist (%s). Leaving.' % BACKUP_ROOT_DIR)
    sys.exit(3)
if not os.path.isdir(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

if BACKUP_TYPE == B_HOURLY:

    # Hourly backups always create new backup files...

    #####
    # 2 #
    #####
    if os.path.exists(BACKUP):
        print('--] Warning. Live backup file exists (%s). Replacing.' % BACKUP)

    #####
    # 3 #
    #####
    BACKUP_START_TIME = datetime.now()
    print('--] Starting backup [%s]' % BACKUP_START_TIME)
    print("    $", BACKUP_CMD)
    COMPLETED_PROCESS = subprocess.run(BACKUP_CMD, shell=True)
    BACKUP_END_TIME = datetime.now()
    print('--] Backup finished [%s]' % BACKUP_END_TIME)
    ELAPSED_TIME = BACKUP_END_TIME - BACKUP_START_TIME
    print('--] Elapsed time %s' % ELAPSED_TIME)

    # Check subprocess exit code
    if COMPLETED_PROCESS.returncode != 0:
        print('--] Backup failed (returncode=%s)' % COMPLETED_PROCESS.returncode)
        if COMPLETED_PROCESS.stderr:
            print('--] stderr follows...')
            COMPLETED_PROCESS.stderr.decode("utf-8")
        sys.exit(0)

    # Now, leave if there is no backup file.
    if not os.path.isfile(BACKUP):
        print('--] No backup file was generated. Leaving.')
        sys.exit(0)

    print('--] Backup size {:,} bytes'.format(os.path.getsize(BACKUP)))

    #####
    # 4 #
    #####
    # The backup time is the start time of this job
    # (but ignore any fractions of a second and then add 'Z'
    # to be very clear that it's UTC.
    BACKUP_TIME = BACKUP_START_TIME.isoformat().split('.')[0] + 'Z'
    COPY_BACKUP_FILE = '%s-%s-%s' % (BACKUP_FILE_PREFIX,
                                     BACKUP_TIME,
                                     BACKUP_LIVE_FILE)
    print('--] Copying %s to %s...' % (BACKUP_LIVE_FILE, COPY_BACKUP_FILE))
    BACKUP_TO = os.path.join(BACKUP_DIR, COPY_BACKUP_FILE)
    shutil.copyfile(BACKUP, BACKUP_TO)
    os.remove(BACKUP)

else:

    #####
    # 5 #
    #####
    # Daily, weekly or monthly backup...
    FILE_SEARCH = os.path.join(BACKUP_PRIOR_DIR, BACKUP_FILE_PREFIX + '*')
    EXISTING_PRIOR_BACKUPS = glob.glob(FILE_SEARCH)
    NUM_PRIOR_BACKUPS = len(EXISTING_PRIOR_BACKUPS)
    if NUM_PRIOR_BACKUPS == BACKUP_PRIOR_COUNT:
        # Prior backup has sufficient files.
        # Copy the oldest
        EXISTING_PRIOR_BACKUPS.sort()
        OLDEST_PRIOR = EXISTING_PRIOR_BACKUPS[0]
        print('--] Copying oldest %s to %s' % (BACKUP_PRIOR_TYPE, BACKUP_DIR))
        print('    %s' % OLDEST_PRIOR)
        shutil.copy2(OLDEST_PRIOR, BACKUP_DIR)
    else:
        print('--] Nothing to do. Too few prior backups (%s). ...' % NUM_PRIOR_BACKUPS)

#####
# 6 #
#####
# Prune files in the current backup directory...
FILE_SEARCH = os.path.join(BACKUP_DIR, BACKUP_FILE_PREFIX + '*')
EXISTING_BACKUPS = glob.glob(FILE_SEARCH)
NUM_TO_DELETE = len(EXISTING_BACKUPS) - BACKUP_COUNT
if NUM_TO_DELETE > 0:
    print('--] Removing expired backups...')
    EXISTING_BACKUPS.sort()
    for EXISTING_BACKUP in EXISTING_BACKUPS[:NUM_TO_DELETE]:
        print('    %s' % EXISTING_BACKUP)
        os.remove(EXISTING_BACKUP)
else:
    print('--] No expired backups to delete')

REMAINING_BACKUPS = glob.glob(FILE_SEARCH)
if REMAINING_BACKUPS:
    print('--] Remaining backups (%s)...' % len(REMAINING_BACKUPS))
    REMAINING_BACKUPS.sort(reverse=True)
    for REMAINING_BACKUP in REMAINING_BACKUPS:
        print('    %s' % REMAINING_BACKUP)

print('--] Done')
