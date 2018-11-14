#!/usr/bin/env python

# A hack module to fixes the attributes file.
#
# Added to fix the standardizer column ordering issue (12 Nov 2018).
# The 3rd column in the attributes file
# (which is incorrectly set to the standardizer's OSMILES column)
# is replaced with the correct value (the supplier ID).
#
# We need: -
#
# -     the broken attributes file
# -     the standardizer directory
#       (expected to contain files named "standardized_*")
#
# Usage: fix_attrs.py attrs_file standardizer_file
#
# The output is a filename that is the same as the attributes file
# but with a '.fixed' suffix, and only lines in it that have a
# supplier ID.

import gzip
import os
import sys

# If set, lines without a corresponding ID are not written.
ONLY_WRITE_LINES_WITH_ID = False

if len(sys.argv) != 3:
    print('Usage: fix_attrs.py <attrs_file> <standardise_dir>')
    sys.exit(1)

attrs_file_name = sys.argv[1]
standardizer_dir = sys.argv[2]
fixed_attrs_file_name = attrs_file_name + '.fixed'

# Input files must exist
if not os.path.isfile(attrs_file_name):
    print('Attributes file (%s) does not exist.' % attrs_file_name)
    sys.exit(1)
if not os.path.isdir(standardizer_dir):
    print('Standardizer directory (%s) does not exist.' % standardizer_dir)
    sys.exit(1)

# Read the OSMILES to map ID from the standardized file
# into memory...
print('Builing id_map from...')
id_map = {}
# Get all the stardardize files
files = os.listdir(standardizer_dir)
for file in files:

    if file.startswith('standardized_'):
        standardizer_file_name = os.path.join(standardizer_dir, file)
        print(' %s', file)
        with gzip.open(standardizer_file_name, 'rb') as s_file:

            line_num = 1
            for line in s_file:
                line_items = line.strip().split()
                if line_num > 1 and len(line_items) == 3:
                    id_map[line_items[1]] = line_items[2]
                line_num += 1

print('Built id_map (%d records)' % len(id_map))

# Read original attrs, writing to the fixed file
print('Writing "%s"...' % fixed_attrs_file_name)
num_lines_written = 0
num_lines_with_id = 0
fixed_file = open(fixed_attrs_file_name, 'w')
with open(attrs_file_name) as a_file:

    for line in a_file:
        line_items = line.strip().split()
        id_field = line_items[-1]
        real_id_value = id_map.get(id_field, None)
        if real_id_value:
            fixed_file.write(" ".join(line_items[:-1]))
            fixed_file.write(" %s\n" % real_id_value)
            num_lines_with_id += 1
            num_lines_written += 1
        elif not ONLY_WRITE_LINES_WITH_ID:
            fixed_file.write(" ".join(line_items[:-1]))
            fixed_file.write("\n")
            num_lines_written += 1

print('Written (%d/%d)' % (num_lines_with_id, num_lines_written))
