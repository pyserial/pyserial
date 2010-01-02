#!/usr/bin/env python
#Python Serial Port Extension for Win32, Linux, BSD, Jython
#see __init__.py
#
#(C) 2001-2003 Chris Liechti <cliechti@gmx.net>
# this is distributed under a free software license, see license.txt

"""Some tests for the serial module.
Part of pyserial (http://pyserial.sf.net)  (C)2002-2003 cliechti@gmx.net

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

# on which port should the tests be performed:
PORT = 0
BAUDRATE = 115200
#~ BAUDRATE=9600

if sys.version_info >= (2, 6):
    bytes_0to255 = bytes(range(256))
else:
    bytes_0to255 = ''.join([chr(x) for x in range(256)])


class TestHighLoad(unittest.TestCase):
    """Test sending and receiving large amount of data"""

    N = 16
    #~ N = 1

    def setUp(self):
        self.s = serial.serial_for_url(PORT, BAUDRATE, timeout=10)

    def tearDown(self):
        self.s.close()

    def test0_WriteReadLoopback(self):
        """Send big strings, write/read order."""
        for i in range(self.N):
            q = bytes_0to255
            self.s.write(q)
            self.failUnlessEqual(self.s.read(len(q)), q) # expected same which was written before
        self.failUnlessEqual(self.s.inWaiting(), 0) # expected empty buffer after all sent chars are read

    def test1_WriteWriteReadLoopback(self):
        """Send big strings, multiple write one read."""
        q = bytes_0to255
        for i in range(self.N):
            self.s.write(q)
        read = self.s.read(len(q)*self.N)
        self.failUnlessEqual(read, q*self.N, "expected what was written before. got %d bytes, expected %d" % (len(read), self.N*len(q)))
        self.failUnlessEqual(self.s.inWaiting(), 0) # "expected empty buffer after all sent chars are read")


if __name__ == '__main__':
    import sys
    sys.stdout.write(__doc__)
    if len(sys.argv) > 1:
        PORT = sys.argv[1]
    sys.stdout.write("Testing port: %r\n" % PORT)
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
