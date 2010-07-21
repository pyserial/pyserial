#! /usr/bin/env python
# Python Serial Port Extension for Win32, Linux, BSD, Jython
# see __init__.py
#
# (C) 2010 Chris Liechti <cliechti@gmx.net>
# this is distributed under a free software license, see license.txt

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
import threading
import time
import sys
import serial

#~ print serial.VERSION

# on which port should the tests be performed:
PORT = 0

if sys.version_info >= (3, 0):
    def data(string):
        return bytes(string, 'latin1')
else:
    def data(string): return string



class Test_Readline(unittest.TestCase):
    """Test readline function"""

    def setUp(self):
        self.s = serial.serial_for_url(PORT, timeout=1)

    def tearDown(self):
        self.s.close()

    def test_readline(self):
        """Test readline method"""
        self.s.write(serial.to_bytes("1\n2\n3\n"))
        self.failUnlessEqual(self.s.readline(), serial.to_bytes("1\n"))
        self.failUnlessEqual(self.s.readline(), serial.to_bytes("2\n"))
        self.failUnlessEqual(self.s.readline(), serial.to_bytes("3\n"))
        # this time we will get a timeout
        self.failUnlessEqual(self.s.readline(), serial.to_bytes(""))

    def test_readlines(self):
        """Test readlines method"""
        self.s.write(serial.to_bytes("1\n2\n3\n"))
        self.failUnlessEqual(
                self.s.readlines(),
                [serial.to_bytes("1\n"), serial.to_bytes("2\n"), serial.to_bytes("3\n")]
                )

    def test_xreadlines(self):
        """Test xreadlines method (skipped for io based systems)"""
        if hasattr(self.s, 'xreadlines'):
            self.s.write(serial.to_bytes("1\n2\n3\n"))
            self.failUnlessEqual(
                    list(self.s.xreadlines()),
                    [serial.to_bytes("1\n"), serial.to_bytes("2\n"), serial.to_bytes("3\n")]
                    )

    def test_for_in(self):
        """Test for line in s"""
        self.s.write(serial.to_bytes("1\n2\n3\n"))
        lines = []
        for line in self.s:
            lines.append(line)
        self.failUnlessEqual(
                lines,
                [serial.to_bytes("1\n"), serial.to_bytes("2\n"), serial.to_bytes("3\n")]
                )

    def test_alternate_eol(self):
        """Test readline with alternative eol settings (skipped for io based systems)"""
        if hasattr(self.s, 'xreadlines'): # test if it is our FileLike base class
            self.s.write(serial.to_bytes("no\rno\nyes\r\n"))
            self.failUnlessEqual(
                    self.s.readline(eol=serial.to_bytes("\r\n")),
                    serial.to_bytes("no\rno\nyes\r\n"))


if __name__ == '__main__':
    import sys
    sys.stdout.write(__doc__)
    if len(sys.argv) > 1:
        PORT = sys.argv[1]
    sys.stdout.write("Testing port: %r\n" % PORT)
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
