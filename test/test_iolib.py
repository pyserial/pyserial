#! /usr/bin/env python
#
# Python Serial Port Extension for Win32, Linux, BSD, Jython
# see __init__.py
#
# (C) 2001-2009 Chris Liechti <cliechti@gmx.net>
# this is distributed under a free software license, see license.txt

"""\
Some tests for the serial module.
Part of pyserial (http://pyserial.sf.net)  (C)2001-2009 cliechti@gmx.net

Intended to be run on different platforms, to ensure portability of
the code.

This modules contains test for the interaction between Serial and the io
library. This only works on Python 2.6+ that introduced the io library.

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

if __name__ == '__main__'  and sys.version_info < (2, 6):
    sys.stderr.write("""\
==============================================================================
WARNING: this test is intended for Python 2.6 and newer where the io library
is available. This seems to be an older version of Python running.
Continuing anyway...
==============================================================================
""")

import io
import serial

# trick to make that this test run under 2.6 and 3.x without modification.
# problem is, io library on 2.6 does NOT accept type 'str' and 3.x doesn't
# like u'nicode' strings with the prefix and it is not providing an unicode
# function ('str' is now what 'unicode' used to be)
if sys.version_info >= (3, 0):
    def unicode(x): return x


# on which port should the tests be performed:
PORT = 0

class Test_SerialAndIO(unittest.TestCase):

    def setUp(self):
        self.s = serial.serial_for_url(PORT, timeout=1)
        self.io = io.TextIOWrapper(io.BufferedRWPair(self.s, self.s))

    def tearDown(self):
        self.s.close()

    def test_hello_raw(self):
        self.io.write(unicode("hello\n"))
        self.io.flush() # it is buffering. required to get the data out
        hello = self.io.readline()
        self.failUnlessEqual(hello, unicode("hello\n"))


if __name__ == '__main__':
    import sys
    sys.stdout.write(__doc__)
    if len(sys.argv) > 1:
        PORT = sys.argv[1]
    sys.stdout.write("Testing port: %r\n" % PORT)
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
