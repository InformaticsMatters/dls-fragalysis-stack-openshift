#!/usr/bin/env python

"""A simple utility to analyse the graph.nf timing files.

Usage:  analyse_timing.py

Alan Christie
July 2018
"""

import glob
from datetime import datetime, timedelta

# Number of slices the analysis is processing.
# With 5,000,000 molecules cut into 2,000 molecule slices
# the number of slices is 2,500.
expected_slices = 2500

# The name of the slice
origin_part = None
# The timestamp of the previous line
prior_line_timestamp = None
# The name of the prior chunk
prior_chunk = None

# Earliest and latest times
earliest_time = None
latest_time = None
# Accumulated de-duplication time
total_deduplication_time = timedelta(0)
num_deduplications = 0
# Accumulated graph time
total_graph_time = timedelta(0)
num_graphs = 0
# Accumulated split time
total_split_time = timedelta(0)
num_splits = 0

# A histogram of chunk durations
histogram = {}
histogram_bin_duration = timedelta(seconds=5)
histogram_max_bin = 0

# A map of interesting chunks and execution time
longest_threshold = timedelta(minutes=1, seconds=30)
longest_chunks = {}


def get_time(line):
    """Get the date/time from the timing line.

    :param line: A single timing log line
    :type line: ``str``
    :returns: A datetime string representation of the time of the line
    :rtype: ``datetime``
    """
    global earliest_time
    global latest_time

    time_part = line.split(',')[1].strip()
    current_time = datetime.strptime(time_part, "%d/%m/%Y %H:%M:%S")
    if not earliest_time or current_time < earliest_time:
        earliest_time = current_time
    if not latest_time or current_time > latest_time:
        latest_time = current_time
    return current_time


def add_chunk_duration(chunk_name, chunk_duration):
    global histogram
    global histogram_max_bin
    global total_graph_time

    bin_index = int(chunk_duration.seconds / histogram_bin_duration.seconds)

    bin_count = histogram.get(bin_index, 0)
    bin_count += 1
    histogram[bin_index] = bin_count
    if bin_index > histogram_max_bin:
        histogram_max_bin = bin_index

    total_graph_time += chunk_duration
    if duration > longest_threshold:
        longest_chunks[chunk_name] = chunk_duration


def dump_histogram():
    global histogram
    global histogram_max_bin

    print('----------------------')
    print(' Chunk-Time Histogram')
    print('----------------------')
    total_count = 0
    bin_start = timedelta(0)
    for bin_index in range(histogram_max_bin + 1):
        count = histogram.get(bin_index, 0)
        total_count += count
        print('%s-%s %6d' % (bin_start, bin_start + histogram_bin_duration, count))
        bin_start += histogram_bin_duration
    print('---------------')
    print('%s-%s %6d' % (timedelta(0), bin_start, total_count))


results_files = glob.glob('results/*.timing')
for results_file in results_files:

    num_graphs += 1

    # Process the log (line by line)...
    with open(results_file) as timing_file:

        line = timing_file.readline()
        while line:

            line_timestamp = get_time(line)

            if line.startswith('doing'):
                # Starting a new smi fragment
                # Reset the prior timestamp.
                prior_line_timestamp = None
                prior_chunk = None
                origin_part = line.split(',')[0].split('-')[1]
            elif line.startswith('done'):
                # completed an smi fragment
                origin_part = None
            elif line.startswith('ligands_part'):
                # Start of a 'chunk'
                # We should have a prior line timestamp
                this_chunk = line.split(',')[0]
                duration = line_timestamp - prior_line_timestamp
                # If no prior chunk then we have a time for
                # the slitting operation
                if not prior_chunk:
                    total_split_time += duration
                    num_splits += 1
                else:
                    # And the identity of the prior 'chunk'
                    chunk_part = origin_part + '/' + prior_chunk
                    add_chunk_duration(chunk_part, duration)
                prior_chunk = this_chunk
            elif line.startswith('deduplicating'):
                # End of chunk processing, start of deduplication
                # We can calculate the duration of the last chunk...
                duration = line_timestamp - prior_line_timestamp
                chunk_part = origin_part + '/' + prior_chunk
                add_chunk_duration(chunk_part, duration)
            elif line.startswith('removing'):
                # Start of file removal
                # We can calculate the deduplication time.
                total_deduplication_time += line_timestamp - prior_line_timestamp
                num_deduplications += 1

            prior_line_timestamp = line_timestamp
            line = timing_file.readline()

dump_histogram()

# Summarise the graph processing time...
print('')
print('Number of graphs: %s' % num_graphs)
print('Total graph time: %s' % total_graph_time)

# Summarise the de-duplication time...
print('')
print('Number of de-duplications:   %s' % num_deduplications)
print('Total de-duplication time:   %s' % total_deduplication_time)
print('Average de-duplication time: %s' % timedelta(seconds=total_deduplication_time.seconds / num_deduplications))

# Summarise the split time...
print('')
print('Number of splits:   %s' % num_splits)
print('Total split time:   %s' % total_split_time)
print('Average split time: %s' % timedelta(seconds=total_split_time.seconds / num_splits))

# Dump any interesting chunk results,
# in order of execution time (duration)
if longest_chunks:
    print('')
    print('Chunks longer than %s (longest first)...' % longest_threshold)
    index = 1
    for chunk, duration in sorted(longest_chunks.items(),
                                  reverse=True,
                                  key=lambda x: x[1]):
        print(' %5d %s %s' % (index, duration, chunk))
        index += 1

print('')
elapsed = latest_time - earliest_time
slice_rate = (float(60) * num_splits / elapsed.seconds)
remaining_time = timedelta(minutes=(expected_slices - num_splits) / slice_rate)
print('Earliest time:  %s (UTC)' % earliest_time)
print('Latest time:    %s (UTC)' % latest_time)
print('Elapsed:        %s' % elapsed)
print('Slice rate:     %s/min' % slice_rate)
print('Remaining time: %s' % remaining_time)
print('ETA:            %s (UTC)' % (latest_time + remaining_time))

