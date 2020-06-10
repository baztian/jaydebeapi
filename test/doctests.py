#!/usr/bin/env python
"""Run doctests."""

import doctest
import platform
import re
import sys

try:
    import unittest2 as unittest
except ImportError:
    import unittest

def _is_new_jpype():
    if platform.python_implementation() != 'Jython':
        import jpype
        try:
            ver_match = re.match('\d+\.\d+', jpype.__version__)
            if ver_match:
                jpype_ver = float(ver_match.group(0))
                if jpype_ver >= 0.7:
                    return True
        except ValueError:
            pass
        return False

class Py23DocChecker(doctest.OutputChecker):
    """Doctest checker to avoid Python 2/3 unicode comparison
    issues. Code mostly taken from Dirkjan Ochtman"""
    def check_output(self, want, got, optionflags):
        if sys.version_info[0] > 2 or _is_new_jpype():
            # new python has unicode as default
            # new JPype does not automatically convert to unicode on Python 2
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
    result = runner.run(suite())
    if result.wasSuccessful():
        return 0
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())
