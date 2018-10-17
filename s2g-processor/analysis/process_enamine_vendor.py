#!/usr/bin/env python

"""process_enamine_vendor.py

Processes Enamine vendor files, not expected to contain pricing information.
Two new files are generated and the original nodes file augmented with
a "V_E" label.

The files generated (in the designated output directory) are:

-   "vendor_nodes.csv.gz"
    containing all the nodes for the vendor compounds.

-   "molecule_vendor_relationships.csv.gz"
    containing the relationships between the original node entries and
    the "Vendor" nodes. There is a relationship for every Enamine
    compound that was found in the earlier processing.

The module also augments the original nodes by adding the label
"V_E".

Alan Christie
October 2018
"""

import argparse
from collections import namedtuple
import glob
import gzip
import os
import re
import sys

# Enamine Columns (space-separated)
#
# SMILES                0
# idnumber              1
# reference             2

# The Vendor node has...
# a UUID
# a compound id
# a smiles string
VendorNode = namedtuple('VendorNode', 'uuid c s')
# The unique set of vendor nodes.
vendor_nodes = set()
# The vendor compound IDs that have a node.
# The index is the compound ID, the value is the VendorNode
vendor_map = {}

# Prefixes for the neo4j node IDs.
vendor_uuid_prefix = 'vne'
# Prefix for output files
output_filename_prefix = 'enamine'

# The next unique ID for a vendor node.
next_vendor_id = 1

# Regular expression to find
# MolPort compound IDs in the original nodes file.
enamine_re = re.compile(r'REAL:(Z\d+)[^\d]')

# Various diagnostic counts
num_nodes = 0
num_nodes_augmented = 0
num_vendor_relationships = 0


def extract_vendor(gzip_filename):
    """Process the given file and extract vendor information.
    """

    global vendor_nodes
    global next_vendor_id

    print('Processing {}...'.format(gzip_filename))

    num_lines = 0
    with gzip.open(gzip_filename, 'rt') as gzip_file:

        # Dump first line (header)
        hdr = gzip_file.readline()

        for line in gzip_file:

            num_lines += 1
            fields = line.split()

            smiles = fields[0]
            compound_id = fields[1].split('Z')[1]
            vendor_node = VendorNode(next_vendor_id, compound_id, smiles)
            vendor_nodes.add(vendor_node)
            vendor_map[compound_id] = vendor_node

            next_vendor_id += 1


def write_vendor_nodes(directory, vendor_nodes):
    """Writes the VendorNodes to a node file, including a header.
    """

    filename = os.path.join(directory,
                            '{}_vendor_nodes.csv.gz'.format(output_filename_prefix))
    print('Writing {}...'.format(filename))

    with gzip.open(filename, 'wb') as gzip_file:
        gzip_file.write(':ID,'
                        'vendor,'
                        'cmpd_id,'
                        'smiles,'
                        ':LABEL\n')
        for vendor_node in vendor_nodes:
            gzip_file.write(
                '{}{},{},{},{},Vendor\n'.format(vendor_uuid_prefix,
                                                vendor_node.uuid,
                                                "Enamine",
                                                vendor_node.c,
                                                vendor_node.s))


def augment_original_nodes(directory, filename, has_header):
    """Augments the original nodes file and writes the relationships
    for nodes in this file to the Vendor nodes.
    """

    global num_nodes
    global num_nodes_augmented
    global num_vendor_relationships

    print('Augmenting {} as...'.format(filename))

    # Augmented file
    augmented_filename =\
        os.path.join(directory,
                     '{}_augmented_{}'.format(output_filename_prefix,
                                              os.path.basename(filename)))
    gzip_ai_file = gzip.open(augmented_filename, 'wt')
    # Frag to Vendor Compound relationships file
    augmented_relationships_filename =\
        os.path.join(directory,
                     '{}_molecule_vendor_relationships.csv.gz'.format(output_filename_prefix))
    gzip_cr_file = gzip.open(augmented_relationships_filename, 'wt')
    gzip_cr_file.write(':START_ID,'
                       ':END_ID,'
                       ':TYPE\n')

    print(' {}'.format(augmented_filename))
    print(' {}'.format(augmented_relationships_filename))

    with gzip.open(filename, 'rt') as gzip_i_file:

        if has_header:
            # Copy first line (header)
            hdr = gzip_i_file.readline()
            gzip_ai_file.write(hdr)

        for line in gzip_i_file:

            num_nodes += 1
            # Search for a potential MolPort identity
            # Get the MolPort compound
            # if we know the compound add a label
            augmented = False
            match_ob = enamine_re.findall(line)
            if match_ob:
                # Look for compounds where we have a costed vendor.
                # If there is one, add the "V_MP" label.
                for compound_id in match_ob:
                    if compound_id in vendor_map:
                        new_line = line.strip() + ';V_E\n'
                        gzip_ai_file.write(new_line)
                        augmented = True
                        num_nodes_augmented += 1
                        break
                if augmented:
                    # If we've augmented the line
                    # append a relationship to the relationships file
                    # for each compound that was found...
                    for compound_id in match_ob:
                        if compound_id in vendor_map:
                            # Now add vendor relationships to this row
                            frag_id = line.split(',')[0]
                            gzip_cr_file.write('{},{}{},HAS_VENDOR\n'.format(frag_id,
                                                                             vendor_uuid_prefix,
                                                                             vendor_map[compound_id].uuid))
                            num_vendor_relationships += 1

            if not augmented:
                # No vendor for this line,
                # just write it out 'as-is'
                gzip_ai_file.write(line)

    # Close augmented nodes and the relationships
    gzip_ai_file.close()
    gzip_cr_file.close()


if __name__ == '__main__':

    parser = argparse.ArgumentParser('Vendor Processor (Enamine)')
    parser.add_argument('dir',
                        help='The Enamine vendor directory,'
                             ' containing the ".gz" files to be processed.'
                             ' All the ".gz" files in the supplied directory'
                             ' will be inspected.')
    parser.add_argument('nodes',
                        help='The nodes file to augment with the collected'
                             ' vendor data')
    parser.add_argument('output',
                        help='The output directory')
    parser.add_argument('--nodes-has-header',
                        help='Use if the nodes file has a header',
                        action='store_true')

    args = parser.parse_args()

    # Create the output directory
    if not os.path.exists(args.output):
        os.mkdir(args.output)
    if not os.path.isdir(args.output):
        print('ERROR: output ({}) is not a directory'.format(args.output))
        sys.exit(1)

    # Process all the files...
    enamine_files = glob.glob('{}/*.gz'.format(args.dir))
    for enamine_file in enamine_files:
        extract_vendor(enamine_file)

    # Write the new nodes and relationships
    # and augment the original nodes file.
    if vendor_map:
        write_vendor_nodes(args.output, vendor_nodes)
        augment_original_nodes(args.output, args.nodes, has_header=args.nodes_has_header)

    # Summary
    print('{} vendor compounds'.format(len(vendor_map)))
    print('{} nodes'.format(num_nodes))
    print('{} augmented nodes'.format(num_nodes_augmented))
    print('{} node vendor relationships'.format(num_vendor_relationships))
