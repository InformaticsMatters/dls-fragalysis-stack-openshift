#!/usr/bin/env python

"""benchmark-neo4j.py

A simple utility that uses the neo4j GraphDatabase module
to submit a series of file-based SMILES strings as queries to neo4j
for benchmarking purposes.

The sequence can be shuffled with an optional externally provided seed.

Run with -h for help.
"""

import argparse
import random
import sys
import time

from neo4j.v1 import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

# The cypher command.
# We'll replace the '%s' instance
# with each SMILES we want to test...
cypher = "MATCH (sta:F2 {smiles:'%s'})-[nm:F2EDGE]-(mid:F2)-[ne:F2EDGE]-(end:EM)" \
         " where  abs(sta.hac-end.hac) <= 3 and abs(sta.chac-end.chac) <= 1" \
         " and sta.smiles <> end.smiles RETURN sta, nm, mid, ne, end" \
         " order by split(nm.label, '|')[4], split(ne.label, '|')[2]"


def run_query(tx, cypher_cmd, smiles_str):
    cypher_str = cypher_cmd % smiles_str
    return tx.run(cypher_str)


def benchmark(smiles_filename, uri, user, password,
              shuffle, shuffle_seed=None):

    # Read SMILES from the supplied input file
    with open(smiles_filename) as smiles_file:
        smiles_set = smiles_file.readlines()
    # And clean up
    smiles_set = [x.strip() for x in smiles_set]
    if shuffle:
        print('Shuffling...')
        if shuffle_seed:
            random.seed(shuffle_seed)
        else:
            seed = str(time.time())
            print('Using new seed: {}'.format(seed))
            random.seed(seed)
        random.shuffle(smiles_set)
        print('Shuffled.')
        print('---')


#    smiles_set = [
#        'CC(C)C(=O)Nc1cccc(C#N)c1',
#        'CN1CCN(c2ccc(C#N)cc2)CC1',
#        'CC(CO)(CO)NC(=O)Nc1ccccc1',
#    ]

    accumulated_time_millis = 0
    accumulated_records = 0
    largest_query = 0
    largest_query_smiles = ''
    longest_query = 0
    longest_query_smiles = ''

    # Connect to neo...
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
    except OSError as e:
        print('Received OSError creating neo4j driver: {}'.format(e))
        sys.exit(1)
    except ServiceUnavailable as e:
        print('Received ServiceUnavailable creating neo4j driver: {}'.format(e))
        sys.exit(1)

    # Iterate through the provided SMILES...
    smiles_num = 1
    with driver.session() as session:
        for smiles in smiles_set:

            # Skip blank lines
            if not smiles:
                continue

            print('{} -> {}'.format(smiles_num, smiles))
            smiles_num += 1
            q_start_time = time.time() * 1000

            results = session.read_transaction(run_query, cypher, smiles)

            q_finish_time = time.time() * 1000
            q_elapsed = int(q_finish_time - q_start_time)
            accumulated_time_millis += q_elapsed

            num_records = 0
            for _ in results:
                num_records += 1
            accumulated_records += num_records
            if num_records > largest_query:
                largest_query = num_records
                largest_query_smiles = smiles

            if q_elapsed > longest_query:
                longest_query = q_elapsed
                longest_query_smiles = smiles

            print(' Records={:,}'.format(num_records))
            print(' Elapsed={:,}mS'.format(q_elapsed))

    # Summarise...

    num_queries = len(smiles_set)
    average_query_time_millis = accumulated_time_millis / num_queries
    average_records = accumulated_records / num_queries
    print('---')
    print('No. SMILES:       {:,}'.format(num_queries))
    print('Total records:    {:,}'.format(accumulated_records))
    print('Avg records:      {:,}'.format(average_records))
    print('Largest query:    {:,} "{}"'.format(largest_query, largest_query_smiles))
    print('Longest query:    {:,}mS "{}"'.format(longest_query, longest_query_smiles))
    print('Total query Time: {:,}S'.format(accumulated_time_millis / 1000))
    print('Avg query Time:   {:,}mS'.format(int(round(average_query_time_millis))))

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='SMILES benchmark for neo4j')
    parser.add_argument('host', type=str, help='The hostname of the neo4j bolt interface,'
                                               ' where port 7687 is available')
    parser.add_argument('user', type=str, help='A valid neo4j user')
    parser.add_argument('password', type=str, help='The neo4j user password')
    parser.add_argument('filename', type=str, help='A file of SMILES')
    parser.add_argument('--shuffle', action='store_true',
                        help='Shuffle the SMILES strings (with an optional seed)')
    parser.add_argument('--seed',
                        help='An optional shuffling seed, useless unless shuffling')
    args = parser.parse_args()

    uri = 'bolt://%s:7687' % args.host
    user = args.user
    password = args.password

    benchmark(args.filename, uri, user, password, args.shuffle, args.seed)
