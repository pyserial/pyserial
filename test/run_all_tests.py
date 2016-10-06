#! /usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2001-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
UnitTest runner. This one searches for all files named test_*.py and collects
all test cases from these files. Finally it runs all tests and prints a
summary.
"""

import unittest
import sys
import os

# inject local copy to avoid testing the installed version instead of the one in the repo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import serial  # noqa
print("Patching sys.path to test local version. Testing Version: {}".format(serial.VERSION))

PORT = 'loop://'
if len(sys.argv) > 1:
    PORT = sys.argv[1]

# find files and the tests in them
mainsuite = unittest.TestSuite()
for modulename in [
        os.path.splitext(x)[0]
        for x in os.listdir(os.path.dirname(__file__) or '.')
        if x != __file__ and x.startswith("test") and x.endswith(".py")
]:
    try:
        module = __import__(modulename)
    except ImportError:
        print("skipping {}".format(modulename))
    else:
        module.PORT = PORT
        testsuite = unittest.findTestCases(module)
        print("found {} tests in {!r}".format(testsuite.countTestCases(), modulename))
        mainsuite.addTest(testsuite)

verbosity = 1
if '-v' in sys.argv[1:]:
    verbosity = 2
    print('-' * 78)

# run the collected tests
testRunner = unittest.TextTestRunner(verbosity=verbosity)
#~ testRunner = unittest.ConsoleTestRunner(verbosity=verbosity)
result = testRunner.run(mainsuite)

# set exit code accordingly to test results
sys.exit(not result.wasSuccessful())
