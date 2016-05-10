#!/usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""
Test PTY related functionality.
"""

import os
import sys

try:
    import pty
except ImportError:
    pty = None
import unittest
import serial


@unittest.skipIf(pty is None, "pty module not supported on platform")
class Test_Pty_Serial_Open(unittest.TestCase):
    """Test PTY serial open"""

    def setUp(self):
        # Open PTY
        self.master, self.slave = pty.openpty()

    def test_pty_serial_open(self):
        """Open serial port on slave"""
        ser = serial.Serial(os.ttyname(self.slave))
        ser.close()


if __name__ == '__main__':
    sys.stdout.write(__doc__)
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
