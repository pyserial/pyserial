#!/usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Test RS485 related functionality.
"""

import unittest
import serial
import serial.rs485

# on which port should the tests be performed:
PORT = 'loop://'


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
        self.assertEqual(self.s._rs485_mode, None, 'RS485 is disabled by default')
        self.assertEqual(self.s.rs485_mode, None, 'RS485 is disabled by default')
        self.s.rs485_mode = serial.rs485.RS485Settings()
        self.assertTrue(self.s._rs485_mode is not None, 'RS485 is enabled')
        self.assertTrue(self.s.rs485_mode is not None, 'RS485 is enabled')
        self.s.rs485_mode = None
        self.assertEqual(self.s._rs485_mode, None, 'RS485 is disabled again')
        self.assertEqual(self.s.rs485_mode, None, 'RS485 is disabled again')


class Test_RS485_class(unittest.TestCase):
    """Test RS485 class"""

    def setUp(self):
        if not isinstance(serial.serial_for_url(PORT), serial.Serial):
            raise unittest.SkipTest("RS485 test only compatible with real serial port")
        self.s = serial.rs485.RS485(PORT, timeout=1)

    def tearDown(self):
        self.s.close()

    def test_RS485_class(self):
        self.s.rs485_mode = serial.rs485.RS485Settings()
        self.s.write(b'hello')
        self.assertEqual(self.s.read(5), b'hello')


if __name__ == '__main__':
    import sys
    sys.stdout.write(__doc__)
    if len(sys.argv) > 1:
        PORT = sys.argv[1]
    sys.stdout.write("Testing port: {!r}\n".format(PORT))
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
