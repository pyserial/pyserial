#! /usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2001-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Some tests for the serial module.
Part of pyserial (https://github.com/pyserial/pyserial)  (C)2001-2009 cliechti@gmx.net

Intended to be run on different platforms, to ensure portability of
the code.

This module contains test for the interaction between Serial and the control of RTS and
DSR signals.

For all these tests a simple hardware is required.
Loopback HW adapter:
Shortcut these pin pairs:
 TX  <-> RX
 RTS <-> CTS
 DTR <-> DSR

On a 9 pole DSUB these are the pins (2-3) (4-6) (7-8)
"""

import unittest
import serial
import time

# on which port should the tests be performed:
PORT = 'loop://'


class Test_RtsDsr(unittest.TestCase):

    def setUp(self):
        self.s = serial.serial_for_url(PORT)

    def tearDown(self):
        self.s.close()

    def test1_RTSDTR(self):
        """Test RTS/CTS"""
        #delay = 1.1
        delay = 0.050

        self.s.write(b"A")
        self.s.flush()

        self.s.rtsdtr = (False,False)
        time.sleep(delay)
        self.assertTrue(not self.s.cts, "CTS -> 0")
        self.assertTrue(not self.s.dsr, "DSR -> 0")

        self.s.rtsdtr = (True,True)
        time.sleep(delay)
        self.assertTrue(self.s.cts, "CTS -> 1")
        self.assertTrue(self.s.dsr, "DSR -> 1")

        self.s.rtsdtr = (False,True)
        time.sleep(delay)
        self.assertTrue(not self.s.cts, "CTS -> 0")
        self.assertTrue(self.s.dsr, "DSR -> 1")

        self.s.rtsdtr = (True,False)
        time.sleep(delay)
        self.assertTrue(self.s.cts, "CTS -> 1")
        self.assertTrue(not self.s.dsr, "DSR -> 0")

        self.s.rtsdtr = (False,False)
        time.sleep(delay)
        self.assertTrue(not self.s.cts, "CTS -> 0")
        self.assertTrue(not self.s.dsr, "DSR -> 0")

        self.s.write(b"B")
        self.s.flush()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    import sys
    sys.stdout.write(__doc__)
    if len(sys.argv) > 1:
        PORT = sys.argv[1]
    sys.stdout.write("Testing port: {!r}\n".format(PORT))
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
