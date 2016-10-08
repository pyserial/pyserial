#!/usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Tests for utility functions of serualutil.
"""

import os
import unittest
import serial


class Test_util(unittest.TestCase):
    """Test serial utility functions"""

    def test_to_bytes(self):
        self.assertEqual(serial.to_bytes([1, 2, 3]), b'\x01\x02\x03')
        self.assertEqual(serial.to_bytes(b'\x01\x02\x03'), b'\x01\x02\x03')
        self.assertEqual(serial.to_bytes(bytearray([1,2,3])), b'\x01\x02\x03')
        # unicode is not supported test. use decode() instead of u'' syntax to be
        # compatible to Python 3.x < 3.4
        self.assertRaises(TypeError, serial.to_bytes, b'hello'.decode('utf-8'))

    def test_iterbytes(self):
        self.assertEqual(list(serial.iterbytes(b'\x01\x02\x03')), [b'\x01', b'\x02', b'\x03'])


if __name__ == '__main__':
    import sys
    sys.stdout.write(__doc__)
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
