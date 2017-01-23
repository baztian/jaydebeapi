#!/usr/bin/env python
"""Run doctests."""

import doctest
import sys

try:
    import unittest2 as unittest
except ImportError:
    import unittest

class Py23DocChecker(doctest.OutputChecker):
    """Doctest checker to avoid Python 2/3 unicode comparison
    issues. Code taken from Dirkjan Ochtman"""
    def check_output(self, want, got, optionflags):
        if sys.version_info[0] > 2:
            want = re.sub("u'(.*?)'", "'\\1'", want)
            want = re.sub('u"(.*?)"', '"\\1"', want)
        return doctest.OutputChecker.check_output(self, want, got, optionflags)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite('../README.rst',
                                       checker=Py23DocChecker()))
    return suite;

def main():
    runner = unittest.TextTestRunner()
    runner.run(suite())

if __name__ == '__main__':
    sys.exit(main())
