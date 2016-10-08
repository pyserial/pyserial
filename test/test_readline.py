#! /usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2010-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Some tests for the serial module.
Part of pyserial (http://pyserial.sf.net)  (C)2010 cliechti@gmx.net

Intended to be run on different platforms, to ensure portability of
the code.

For all these tests a simple hardware is required.
Loopback HW adapter:
Shortcut these pin pairs:
 TX  <-> RX
 RTS <-> CTS
 DTR <-> DSR

On a 9 pole DSUB these are the pins (2-3) (4-6) (7-8)
"""

import unittest
import sys
import serial

#~ print serial.VERSION

# on which port should the tests be performed:
PORT = 'loop://'

if sys.version_info >= (3, 0):
    def data(string):
        return bytes(string, 'latin1')
else:
    def data(string):
        return string


class Test_Readline(unittest.TestCase):
    """Test readline function"""

    def setUp(self):
        self.s = serial.serial_for_url(PORT, timeout=1)

    def tearDown(self):
        self.s.close()

    def test_readline(self):
        """Test readline method"""
        self.s.write(serial.to_bytes([0x31, 0x0a, 0x32, 0x0a, 0x33, 0x0a]))
        self.assertEqual(self.s.readline(), serial.to_bytes([0x31, 0x0a]))
        self.assertEqual(self.s.readline(), serial.to_bytes([0x32, 0x0a]))
        self.assertEqual(self.s.readline(), serial.to_bytes([0x33, 0x0a]))
        # this time we will get a timeout
        self.assertEqual(self.s.readline(), serial.to_bytes([]))

    def test_readlines(self):
        """Test readlines method"""
        self.s.write(serial.to_bytes([0x31, 0x0a, 0x32, 0x0a, 0x33, 0x0a]))
        self.assertEqual(
                self.s.readlines(),
                [serial.to_bytes([0x31, 0x0a]), serial.to_bytes([0x32, 0x0a]), serial.to_bytes([0x33, 0x0a])]
                )

    def test_xreadlines(self):
        """Test xreadlines method (skipped for io based systems)"""
        if hasattr(self.s, 'xreadlines'):
            self.s.write(serial.to_bytes([0x31, 0x0a, 0x32, 0x0a, 0x33, 0x0a]))
            self.assertEqual(
                    list(self.s.xreadlines()),
                    [serial.to_bytes([0x31, 0x0a]), serial.to_bytes([0x32, 0x0a]), serial.to_bytes([0x33, 0x0a])]
                    )

    def test_for_in(self):
        """Test for line in s"""
        self.s.write(serial.to_bytes([0x31, 0x0a, 0x32, 0x0a, 0x33, 0x0a]))
        lines = []
        for line in self.s:
            lines.append(line)
        self.assertEqual(
                lines,
                [serial.to_bytes([0x31, 0x0a]), serial.to_bytes([0x32, 0x0a]), serial.to_bytes([0x33, 0x0a])]
                )

    def test_alternate_eol(self):
        """Test readline with alternative eol settings (skipped for io based systems)"""
        if hasattr(self.s, 'xreadlines'):  # test if it is our FileLike base class
            self.s.write(serial.to_bytes("no\rno\nyes\r\n"))
            self.assertEqual(
                    self.s.readline(eol=serial.to_bytes("\r\n")),
                    serial.to_bytes("no\rno\nyes\r\n"))


if __name__ == '__main__':
    import sys
    sys.stdout.write(__doc__)
    if len(sys.argv) > 1:
        PORT = sys.argv[1]
    sys.stdout.write("Testing port: {!r}\n".format(PORT))
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
