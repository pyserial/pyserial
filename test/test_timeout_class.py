#!/usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""
Test Timeout helper class.
"""
import sys
import unittest
import time
from serial import serialutil


class TestTimeoutClass(unittest.TestCase):
    """Test the Timeout class"""

    def test_simple_timeout(self):
        """Test simple timeout"""
        t = serialutil.Timeout(2)
        self.assertFalse(t.expired())
        self.assertTrue(t.time_left() > 0)
        time.sleep(2.1)
        self.assertTrue(t.expired())
        self.assertEqual(t.time_left(), 0)

    def test_non_blocking(self):
        """Test nonblocking case (0)"""
        t = serialutil.Timeout(0)
        self.assertTrue(t.is_non_blocking)
        self.assertFalse(t.is_infinite)
        self.assertTrue(t.expired())

    def test_blocking(self):
        """Test no timeout (None)"""
        t = serialutil.Timeout(None)
        self.assertFalse(t.is_non_blocking)
        self.assertTrue(t.is_infinite)
        #~ self.assertFalse(t.expired())

    def test_changing_clock(self):
        """Test recovery from chaning clock"""
        class T(serialutil.Timeout):
            def TIME(self):
                return test_time
        test_time = 1000
        t = T(10)
        self.assertEqual(t.target_time, 1010)
        self.assertFalse(t.expired())
        self.assertTrue(t.time_left() > 0)
        test_time = 100  # clock jumps way back
        self.assertTrue(t.time_left() > 0)
        self.assertTrue(t.time_left() <= 10)
        self.assertEqual(t.target_time, 110)
        test_time = 10000  # jump way forward
        self.assertEqual(t.time_left(), 0)  # if will expire immediately


if __name__ == '__main__':
    sys.stdout.write(__doc__)
    if len(sys.argv) > 1:
        PORT = sys.argv[1]
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
