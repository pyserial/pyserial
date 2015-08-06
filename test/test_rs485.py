#!/usr/bin/env python

# Python Serial Port Extension for Win32, Linux, BSD, Jython
# see __init__.py
#
# (C) 2015 Chris Liechti <cliechti@gmx.net>
# this is distributed under a free software license, see license.txt

"""\
Test RS485 related functionality.
"""

import unittest
import serial
import serial.rs485

# on which port should the tests be performed:
PORT = 0

class Test_RS485_settings(unittest.TestCase):
    """Test RS485 related functionality"""

    def setUp(self):
        # create a closed serial port
        self.s = serial.serial_for_url(PORT, do_not_open=True)

    def tearDown(self):
        self.s.close()

    def test_enable_RS485(self):
        # XXX open() port - but will result in fail for most HW...
        #~ self.s.open()
        self.failUnlessEqual(self.s._rs485_mode, None, 'RS485 is disabled by default')
        self.failUnlessEqual(self.s.rs485_mode, None, 'RS485 is disabled by default')
        self.s.rs485_mode = serial.rs485.RS485Settings()
        self.failUnless(self.s._rs485_mode is not None, 'RS485 is enabled')
        self.failUnless(self.s.rs485_mode is not None, 'RS485 is enabled')
        self.s.rs485_mode = None
        self.failUnlessEqual(self.s._rs485_mode, None, 'RS485 is disabled again')
        self.failUnlessEqual(self.s.rs485_mode, None, 'RS485 is disabled again')


class Test_RS485_class(unittest.TestCase):
    """Test RS485 class"""

    def setUp(self):
        self.s = serial.rs485.RS485(PORT, timeout=3)

    def tearDown(self):
        self.s.close()

    def test_RS485_class(self):
        self.s.rs485_mode = serial.rs485.RS485Settings()
        self.s.write(b'hello')
        self.failUnlessEqual(self.s.read(5), b'hello')



if __name__ == '__main__':
    import sys
    sys.stdout.write(__doc__)
    if len(sys.argv) > 1:
        PORT = sys.argv[1]
    sys.stdout.write("Testing port: %r\n" % PORT)
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
