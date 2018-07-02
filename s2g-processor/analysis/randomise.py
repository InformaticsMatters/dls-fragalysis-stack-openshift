#!/usr/bin/env python

"""
Given a SMILES file, the number of SMILES in it
and the number of SMILES required this module writes
a random selection of SMILES from the original file
to the original file with ".random" appended to the name.

The input file is expected to have a header, which is copied
to the output.
"""

import argparse
import random
import sys
from datetime import datetime

parser = argparse.ArgumentParser(description='SMILES randomiser.'
                                 ' Given a SMILES file this utility'
                                 ' writes a random selection of lines'
                                 ' to stdout.')
parser.add_argument('file_name',
                    help='The name of your SMILES file. The output will be'
                         ' written a file of this name with the value'
                         ' ".random-M-N" appended, where M is the output_size'
                         ' and N is the random seed.')
parser.add_argument('input_size',
                    help='The number of molecules in the file.'
                         ' The number here can be smaller than the'
                         ' number of SMILES, but not larger.',
                    type=int)
parser.add_argument('output_size',
                    help='The random number of molecules you want.'
                         ' This must not be larger than the input size.',
                    type=int)
parser.add_argument("--seed",
                    help="The random seed. If not defined the hash of the"
                         " current time is used, and printed",
                    type=int)
args = parser.parse_args()

# Sanity checks...
if args.input_size < 1 or args.output_size < 1:
    print('ERROR: Input or output size is invalid.')
    parser.print_usage()
    sys.exit(1)
if args.output_size >= args.input_size:
    print('ERROR: Output size must be less than the input size.')
    parser.print_usage()
    sys.exit(1)

# A random selection from all possible possible lines...

print('Generating line selection...')

# User provided seed or a new one?
if args.seed:
    seed_value = args.seed
else:
    seed_value = abs(hash(datetime.now()))
print("# random.seed(%s)" % seed_value)
random.seed(seed_value)

input_size_minus_header = args.input_size - 1
line_selection = sorted(set(random.sample(xrange(1, input_size_minus_header + 1),
                                          args.output_size)))
print('Generated')

# Output file...
output_filename = args.file_name + ".random-%d-%d" % (args.output_size, seed_value)
output_file = open(output_filename, 'w')

print('Writing...')
print('# to "%s"' % output_filename)

# Read file, dropping each line until we reach the line in the selection.
# Once met, print and move to the next selection.
source_line_num = 0
line_selection_index = 0
with open(args.file_name) as smiles_file:

    # Fist line is special always copy this (it's the header)
    line = smiles_file.readline()
    output_file.write(line.strip() + '\n')

    # Until we've written the required number of SMILES
    # read the input file until the line counter meets the
    # next index into the list of randomly selected lines.
    while line_selection_index < args.output_size:

        line = smiles_file.readline()
        if line:
            source_line_num += 1
            if source_line_num == line_selection[line_selection_index]:
                output_file.write(line.strip() + '\n')
                line_selection_index += 1

output_file.close()

print('Written')
