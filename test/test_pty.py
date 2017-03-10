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

DATA = b'Hello\n'

@unittest.skipIf(pty is None, "pty module not supported on platform")
class Test_Pty_Serial_Open(unittest.TestCase):
    """Test PTY serial open"""

    def setUp(self):
        # Open PTY
        self.master, self.slave = pty.openpty()

    def test_pty_serial_open_slave(self):
        with serial.Serial(os.ttyname(self.slave), timeout=1) as slave:
            pass  # OK

    def test_pty_serial_write(self):
        with serial.Serial(os.ttyname(self.slave), timeout=1) as slave:
            with os.fdopen(self.master, "wb") as fd:
                fd.write(DATA)
                fd.flush()
                out = slave.read(len(DATA))
                self.assertEqual(DATA, out)

    def test_pty_serial_read(self):
        with serial.Serial(os.ttyname(self.slave), timeout=1) as slave:
            with os.fdopen(self.master, "rb") as fd:
                slave.write(DATA)
                slave.flush()
                out = fd.read(len(DATA))
                self.assertEqual(DATA, out)

if __name__ == '__main__':
    sys.stdout.write(__doc__)
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
