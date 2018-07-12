#!/usr/bin/env python

"""A simple utility to analyse Nextflow log files in order to determine the
duration of the `graph` execution times of the job.
Run Nextflow and then run this utility, which expects (by default)
to find a `.nextflow.log` file in the current directory.

Usage:  analyse_nf_graph.py -h

Alan Christie
July 2018
"""

import argparse
import re
from datetime import datetime, timedelta

# RegEx for the Graph's Job ID in a Nextflow log-line.
RE_GRAPH_ID = '.* graph \((\d+)\).*'

PARSER = argparse.ArgumentParser(description='Graph construction analyser.'
                                 ' Analyses Nextflow logfile that was used'
                                 ' for Graph processing.')
PARSER.add_argument('-l', '--logfile',
                    nargs='?', default='.nextflow.log',
                    help='The file to analyse')
PARSER.add_argument('-d', '--detail',
                    action='store_true',
                    help='Include detailed job timings using a CSV-style'
                         ' of output')
ARGS = PARSER.parse_args()

LOG_FILE_NAME = ARGS.logfile


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


TOTAL_START = None
TOTAL_STOP = None
MOST_RECENT_COMPLETED_TIME = None
GRAPH_START_TIMES = {}
GRAPH_DURATIONS = {}
NUM_RUNNING = 0

# Process the log (line by line)...
with open(LOG_FILE_NAME) as log_file:

    LINE = log_file.readline()

    if not TOTAL_START and LINE and 'nextflow.cli.Launcher' in LINE:
        TOTAL_START = get_time(LINE)

    # Find graph container durations
    while LINE:

        if 'Submitted' in LINE and 'graph' in LINE:
            G_ID = get_graph_id(LINE)
            GRAPH_START_TIMES[G_ID] = get_time(LINE)
            NUM_RUNNING += 1
        elif 'COMPLETED' in LINE and 'graph' in LINE:
            NUM_RUNNING -= 1
            G_ID = get_graph_id(LINE)
            if G_ID in GRAPH_START_TIMES:
                MOST_RECENT_COMPLETED_TIME = get_time(LINE)
                GRAPH_DURATION = MOST_RECENT_COMPLETED_TIME - GRAPH_START_TIMES[G_ID]
                GRAPH_DURATIONS[G_ID] = GRAPH_DURATION
                if ARGS.detail:
                    print('%d,%s' % (G_ID, GRAPH_DURATION))
        elif not TOTAL_STOP and 'Goodbye' in LINE:
            TOTAL_STOP = get_time(LINE)

        LINE = log_file.readline()

# Summarise the results...
if TOTAL_START:
    print("Process start time = %s" % TOTAL_START)
    if MOST_RECENT_COMPLETED_TIME:
        print("Most recent        = %s" % MOST_RECENT_COMPLETED_TIME)
        print("Duration so far    = %s" % (MOST_RECENT_COMPLETED_TIME - TOTAL_START))
# Collect graph results
# Keeping longest, shortest and total.
TOTAL_DURATION = timedelta(0)
SHORTEST_DURATION = None
LONGEST_DURATION = None
for G_ID in GRAPH_DURATIONS:
    G_DURATION = GRAPH_DURATIONS[G_ID]
    if SHORTEST_DURATION is None or G_DURATION < SHORTEST_DURATION:
        SHORTEST_DURATION = G_DURATION
    if LONGEST_DURATION is None or G_DURATION > LONGEST_DURATION:
        LONGEST_DURATION = G_DURATION
    TOTAL_DURATION += G_DURATION
print("Graphs complete    = %d" % len(GRAPH_DURATIONS))
print("Graphs running now = %d" % NUM_RUNNING)
if TOTAL_DURATION:
    print("Longest  duration  = %s" % LONGEST_DURATION)
    print("Shortest duration  = %s" % SHORTEST_DURATION)
    print("Average duration   = %s" % str((TOTAL_DURATION / len(GRAPH_DURATIONS))).split('.')[0])
# And the total execution time?
if TOTAL_START and TOTAL_STOP:
    print("End-2-end duration = %s" % str(TOTAL_STOP - TOTAL_START))
elif not TOTAL_START:
    print("End-2-end duration = It's not started")
elif not TOTAL_STOP:
    print("End-2-end duration = It's not stopped")
