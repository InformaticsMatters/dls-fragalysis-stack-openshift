#!/usr/bin/env python

"""A simple utility to analyse Nextflow log files in order to determine the
duration of the `split` and `graph` execution times of the `nf_ena`
code. Run Nextflow and then run this utility (which expects the `.nextflow.log`
file to be in the current working directory) in order to get the execution
time of the `split` operation and the shortest, longest amd average length of
the graph executions.

Usage:  analyse_nf_graph.py [log filename]

Alan Christie
July 2018
"""

import sys
import re
from datetime import datetime, timedelta

# RegEx for the Graoh's ID in a long-line.
RE_GRAPH_ID = '.* graph \((\d+)\).*'

if len(sys.argv) > 2:
    print('ERROR: Expected log filensme')
    print('Usage: analyse_nf_graph.py [log filename]')
    sys.exit(1)

# Default Nextflow logfile or user-provided?
if len(sys.argv) == 2:
    log_file_name = sys.argv[1]
else:
    log_file_name = '.nextflow.log'


def get_time(nf_line):
    """Get the date/time from the log.
    Sadly the log does not contain the year so this can only be
    used for relative timings that don't cross New Year's Eve.

    :param nf_line: A single Nextflow log line
    :type nf_line: ``str``
    :returns: A datetime string representation of the time of the line
    ":rtype: ``datetime``
    """
    fields = nf_line.split()
    if len(fields) > 2:
        dt_str = fields[0] + " " + fields[1]
        return datetime.strptime(dt_str[:-4], "%b-%d %H:%M:%S")
    return None


def get_graph_id(nf_line):
    """Get the Graph identity from the log.

    :param nf_line: A single Nextflow log line
    :type nf_line: ``str``
    :returns: The graph Id or 0
    :rtype: ``int``
    """
    match_ob = re.match(RE_GRAPH_ID, nf_line)
    if match_ob:
        return int(match_ob.group(1))
    return 0


total_start = None
total_stop = None
sdsplit_start = None
sdsplit_stop = None
sdsplit_duration = None
graph_start_durations = {}
graph_durations = {}

# Process the log (line by line)...
with open(log_file_name) as log_file:

    line = log_file.readline()

    if not total_start and line and 'nextflow.cli.Launcher' in line:
        total_start = get_time(line)

    # Find sdsplit duration
    while line and not sdsplit_stop:

        if 'Creating operator > sdsplit' in line:
            sdsplit_start = get_time(line)
        elif 'sdsplit' in line and 'COMPLETED' in line:
            sdsplit_stop = get_time(line)

        line = log_file.readline()

    if sdsplit_stop and sdsplit_start:
        sdsplit_duration = sdsplit_stop - sdsplit_start

    # Find graph container durations
    while line:

        if 'Submitted' in line and 'graph' in line:
            g_id = get_graph_id(line)
            graph_start_durations[g_id] = get_time(line)
        elif 'COMPLETED' in line and 'graph' in line:
            g_id = get_graph_id(line)
            if g_id in graph_start_durations:
                graph_durations[g_id] = get_time(line) - graph_start_durations[g_id]
        elif not total_stop and 'Goodbye' in line:
            total_stop = get_time(line)

        line = log_file.readline()

log_file.close()

if not sdsplit_duration:
    print("Couldn't determine SD Split duration (has it finished?)")
    sys.exit(0)

# Summarise the results...
print("SD Split Duration  = %s" % sdsplit_duration)
# Collect graph results
# Keeping longest, shortest and total.
total_duration = timedelta(0)
shortest_duration = None
longest_duration = None
for g_id in graph_durations:
    g_duration = graph_durations[g_id]
    if shortest_duration is None or g_duration < shortest_duration:
        shortest_duration = g_duration
    if longest_duration is None or g_duration > longest_duration:
        longest_duration = g_duration
    total_duration += g_duration
print("Number of graphs  = %d" % len(graph_durations))
if total_duration:
    print("Longest  duration  = %s" % longest_duration)
    print("Shortest duration  = %s" % shortest_duration)
    print("Average duration   = %s" % str((total_duration / len(graph_durations))).split('.')[0])
# And the total execution time?
if total_start and total_stop:
    print("End-2-end duration = %s" % str(total_stop - total_start))
elif not total_start:
    print("End-2-end duration = It's not started")
elif not total_stop:
    print("End-2-end duration = It's not stopped")
