#!/usr/bin/env python

"""
Given a SMILES file, the number of SMILES in it
and the number of SMILES required this module writes
a random selection of SMILES from the original file
to the original file with ".random-M-N" appended to the name.
Where M is the number of SMILES written and N is the random seed
used to select them.

The input file is expected to have a header, which is copied
to the output.

A typical execution, selecting a million random samples from
a file of 39,765,321 molecules, would be: -

./randomise.py \
  ~/Downloads/Jun2018_REAL_analogs_DSI_library_39M_MW_HA_smiles_clean.smiles \
  39765321 1000000

Alan Christie
July 2018
"""

import argparse
import random
import sys
from datetime import datetime

PARSER = argparse.ArgumentParser(description='SMILES randomiser.'
                                 ' Given a SMILES file this utility'
                                 ' writes a random selection of lines'
                                 ' to stdout.')
PARSER.add_argument('file_name',
                    help='The name of your SMILES file. The output will be'
                         ' written a file of this name with the value'
                         ' ".random-M-N" appended, where M is the output_size'
                         ' and N is the random seed.')
PARSER.add_argument('input_size',
                    help='The number of molecules in the file.'
                         ' The number here can be smaller than the'
                         ' number of SMILES, but not larger.',
                    type=int)
PARSER.add_argument('output_size',
                    help='The random number of molecules you want.'
                         ' This must not be larger than the input size.',
                    type=int)
PARSER.add_argument('--seed',
                    help='The random seed. If not defined the hash of the'
                         ' current time is used, and printed',
                    type=int)
ARGS = PARSER.parse_args()

# Sanity checks...
if ARGS.input_size < 1 or ARGS.output_size < 1:
    print('ERROR: Input or output size is invalid.')
    PARSER.print_usage()
    sys.exit(1)
if ARGS.output_size >= ARGS.input_size:
    print('ERROR: Output size must be less than the input size.')
    PARSER.print_usage()
    sys.exit(1)

# A random selection from all possible possible lines...

print('Generating line selection...')

# User provided seed or a new one?
if ARGS.seed:
    seed_value = ARGS.seed
else:
    seed_value = abs(hash(datetime.now()))
print("# random.seed(%s)" % seed_value)
random.seed(seed_value)

INPUT_SIZE_MINUS_HEADER = ARGS.input_size - 1
LINE_SELECTION = sorted(set(random.sample(range(1, INPUT_SIZE_MINUS_HEADER + 1),
                                          ARGS.output_size)))
print('Generated')

# Output file...
OUTPUT_FILENAME = ARGS.file_name + ".random-%d-%d" % (ARGS.output_size, seed_value)
OUTPUT_FILE = open(OUTPUT_FILENAME, 'w')

print('Writing...')
print('# to "%s"' % OUTPUT_FILENAME)

# Read file, dropping each line until we reach the line in the selection.
# Once met, print and move to the next selection.
SOURCE_LINE_NUM = 0
LINE_SELECTION_INDEX = 0
with open(ARGS.file_name) as smiles_file:

    # Fist line is special always copy this (it's the header)
    LINE = smiles_file.readline()
    OUTPUT_FILE.write(LINE.strip() + '\n')

    # Until we've written the required number of SMILES
    # read the input file until the line counter meets the
    # next index into the list of randomly selected lines.
    while LINE_SELECTION_INDEX < ARGS.output_size:

        LINE = smiles_file.readline()
        if LINE:
            SOURCE_LINE_NUM += 1
            if SOURCE_LINE_NUM == LINE_SELECTION[LINE_SELECTION_INDEX]:
                OUTPUT_FILE.write(LINE.strip() + '\n')
                LINE_SELECTION_INDEX += 1

OUTPUT_FILE.close()

print('Written')
