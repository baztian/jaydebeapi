#!/bin/env/python

"""Runs coveralls if in Travis CI build environment. Taken from
http://stackoverflow.com/a/33012308/1960601
"""

import os
import sys

from subprocess import call


if __name__ == '__main__':
    if sys.platform.lower().startswith('java'):
        print("Export to coveralls skipped for Jython")
        sys.exit(0)
    if 'TRAVIS' in os.environ:
        rc = call('coveralls')
        raise SystemExit(rc)
