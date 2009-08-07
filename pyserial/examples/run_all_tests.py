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

PORT = 'loop://'

# find files and the tests in them
mainsuite = unittest.TestSuite()
for modulename in [os.path.splitext(x)[0]
    for x in os.listdir('.')
        if x != __file__ and x.startswith("test_") and x.endswith(".py")
]:
    try:
        module = __import__(modulename)
    except ImportError:
        print "skipping %s" % modulename
    else:
        module.PORT = PORT
        testsuite = unittest.findTestCases(module)
        print "found %s tests in %r" % (testsuite.countTestCases(), modulename)
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
