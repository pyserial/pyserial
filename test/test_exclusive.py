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
        if not isinstance(serial.serial_for_url(PORT), serial.Serial):
            raise unittest.SkipTest("exclusive test only compatible with real serial port")

    @unittest.skipIf(os.name != 'posix', "exclusive setting not supported on platform")
    def test_exclusive(self):
        """test if port can be opened twice"""
        a = serial.Serial(PORT, exclusive=True)
        with self.assertRaises(serial.SerialException):
            b = serial.Serial(PORT, exclusive=True)


if __name__ == '__main__':
    sys.stdout.write(__doc__)
    if len(sys.argv) > 1:
        PORT = sys.argv[1]
    sys.stdout.write("Testing port: {!r}\n".format(PORT))
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
