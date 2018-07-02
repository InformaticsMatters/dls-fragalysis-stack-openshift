#!/usr/bin/env python

"""yaml2json.py

Convert a YAML file to a JSON file. The utility expects YAML text on STDIN
and writes JSON to STDOUT. Typical execution would be: -

    ./yaml2json.py < yaml-file > json-file
"""

import json
import sys
import yaml

# just read the YAML file with yaml.load...
# and write out using json.dump
sys.stdout.write(json.dumps(yaml.load(sys.stdin), indent=2))
