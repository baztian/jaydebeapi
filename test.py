#!/usr/bin/env python
"""Run unittests in the `tests` directory."""

import os
import sys

def adjust_sys_path(dir_name='libs'):
    """
    Patch to search the libs folder. At the moment, I believe it's unable to
    find .egg's, but it does search libs for imports before anything else.
    """
    root_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(root_dir, dir_name))

adjust_sys_path('libs')
adjust_sys_path('src')

import unittest2

def main():
    suite = unittest2.loader.TestLoader().discover('src/test')
    unittest2.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    main()
