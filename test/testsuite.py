#!/usr/bin/env python
"""Run unittests in the `tests` directory."""

from optparse import OptionParser
import sys

try:
    import unittest2 as unittest
except ImportError:
    import unittest

def main():
    parser = OptionParser()
    parser.add_option("-x", "--xml", action="store_true", dest="xml",
                  help="write test report in xunit file format (requires xmlrunner==1.7.4)")
    (options, args) = parser.parse_args(sys.argv)
    loader = unittest.defaultTestLoader
    names = args[1:]
    if names:
        suite = loader.loadTestsFromNames(names)
    else:
        suite = loader.discover('test')
    if options.xml:
        import xmlrunner
        runner = xmlrunner.XMLTestRunner(output='build/test-reports')
    else:
        runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        return 0
    else:
        return 1
    
if __name__ == '__main__':
    sys.exit(main())
