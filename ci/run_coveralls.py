#!/bin/env/python

"""Runs coveralls if in Travis CI build environment. Taken from
http://stackoverflow.com/a/33012308/1960601
"""

import json
import os
import pickle
import sys

from subprocess import call

def convert_old_coverage_to_new(filename):
    with open(filename, "rb") as inp_file:
        coverage_results = pickle.load(inp_file)
    main_results ={"lines": coverage_results['lines']}
    with open(".coverage","w") as out_file:
        out_file.write("!coverage.py: This is a private format,"
                       "don't read it directly!")
        out_file.write(json.dumps(main_results))

if __name__ == '__main__':
    if sys.platform.lower().startswith('java'):
        convert_old_coverage_to_new(".coverage")
    if 'TRAVIS' in os.environ:
        rc = call('coveralls')
        raise SystemExit(rc)
