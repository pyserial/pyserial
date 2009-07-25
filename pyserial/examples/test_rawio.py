##! /usr/bin/env python
# Python Serial Port Extension for Win32, Linux, BSD, Jython
# see __init__.py
#
# (C) 2001-2008 Chris Liechti <cliechti@gmx.net>
# this is distributed under a free software license, see license.txt

"""\
Some tests for the serial module.
Part of pyserial (http://pyserial.sf.net)  (C)2001-2009 cliechti@gmx.net

Intended to be run on different platforms, to ensure portability of
the code.

This modules contains test for RawSerial. This only works on Python 2.6+ with
the io library.

For all these tests a simple hardware is required.
Loopback HW adapter:
Shortcut these pin pairs:
 TX  <-> RX
 RTS <-> CTS
 DTR <-> DSR

On a 9 pole DSUB these are the pins (2-3) (4-6) (7-8)
"""

import unittest, threading, time
import serial

# on which port should the tests be performed:
PORT=0

class Test_RawSerial(unittest.TestCase):

    def setUp(self):
        self.s = serial.RawSerial(PORT)

    def tearDown(self):
        self.s.close()

    def test_hello(self):
        self.s.write(bytes("hello"))
        hello = self.s.read(5)
        #~ print hello
        self.failUnlessEqual(hello, bytes("hello"))


if __name__ == '__main__':
    import sys
    sys.stdout.write(__doc__)
    if len(sys.argv) > 1:
        PORT = sys.argv[1]
    sys.stdout.write("Testing port: %r\n" % PORT)
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
