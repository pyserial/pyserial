#!/usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2017 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Tests for exclusive access feature.
"""

import os
import unittest
import sys
import serial

# on which port should the tests be performed:
PORT = 'loop://'

class Test_exclusive(unittest.TestCase):
    """Test serial port locking"""

    def setUp(self):
        with serial.serial_for_url(PORT, do_not_open=True) as x:
            if not isinstance(x, serial.Serial):
                raise unittest.SkipTest("exclusive test only compatible with real serial port")

    def test_exclusive_none(self):
        """test for exclusive=None"""
        with serial.Serial(PORT, exclusive=None):
            pass  # OK

    @unittest.skipUnless(os.name == 'posix', "exclusive=False not supported on platform")
    def test_exclusive_false(self):
        """test for exclusive=False"""
        with serial.Serial(PORT, exclusive=False):
            pass  # OK

    @unittest.skipUnless(os.name in ('posix', 'nt'), "exclusive=True setting not supported on platform")
    def test_exclusive_true(self):
        """test for exclusive=True"""
        with serial.Serial(PORT, exclusive=True):
            with self.assertRaises(serial.SerialException):
                serial.Serial(PORT, exclusive=True)  # fails to open twice

    @unittest.skipUnless(os.name == 'nt', "platform is not restricted to exclusive=True (and None)")
    def test_exclusive_only_true(self):
        """test if exclusive=False is not supported"""
        with self.assertRaises(ValueError):
            serial.Serial(PORT, exclusive=False) # expected to fail: False not supported


if __name__ == '__main__':
    sys.stdout.write(__doc__)
    if len(sys.argv) > 1:
        PORT = sys.argv[1]
    sys.stdout.write("Testing port: {!r}\n".format(PORT))
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
