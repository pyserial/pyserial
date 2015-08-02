#! /usr/bin/env python

"""\
UnitTest runner. This one searches for all files named test_*.py and collects
all test cases from these files. Finally it runs all tests and prints a
summary.
"""

import unittest
import sys
import os
import time

# inject local copy to avoid testing the installed version instead of the
# working copy (only for 2.x as the sources would need to be translated with
# 2to3 for Python 3, use installed module instead for Python 3).
if sys.version_info < (3, 0):
    sys.path.insert(0, '..')

import serial
print("Patching sys.path to test local version. Testing Version: %s" % (serial.VERSION,))

PORT = 'loop://'
if len(sys.argv) > 1:
    PORT = sys.argv[1]

# find files and the tests in them
mainsuite = unittest.TestSuite()
for modulename in [os.path.splitext(x)[0]
    for x in os.listdir('.')
        if x != __file__ and x.startswith("test") and x.endswith(".py")
]:
    try:
        module = __import__(modulename)
    except ImportError:
        print("skipping %s" % (modulename,))
    else:
        module.PORT = PORT
        testsuite = unittest.findTestCases(module)
        print("found %s tests in %r" % (testsuite.countTestCases(), modulename))
        mainsuite.addTest(testsuite)

verbosity = 1
if '-v' in sys.argv[1:]:
    verbosity = 2

# run the collected tests
testRunner = unittest.TextTestRunner(verbosity=verbosity)
#~ testRunner = unittest.ConsoleTestRunner(verbosity=verbosity)
result = testRunner.run(mainsuite)

# set exit code accordingly to test results
sys.exit(not result.wasSuccessful())
