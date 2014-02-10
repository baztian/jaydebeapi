#!/usr/bin/env python
"""Run unittests in the `tests` directory."""

from optparse import OptionParser
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
    parser = OptionParser()
    parser.add_option("-x", "--xml", action="store_true", dest="xml",
                  help="write test report in xunit file format")
    (options, args) = parser.parse_args(sys.argv)
    suite = unittest2.loader.TestLoader().discover('src/test')
    if options.xml:
        import xmlrunner
        runner = xmlrunner.XMLTestRunner(output='build/test-reports')
    else:
        runner = unittest2.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        return 0
    else:
        return 1
    
if __name__ == '__main__':
    sys.exit(main())
