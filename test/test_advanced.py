#!/usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2001-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Some tests for the serial module.
Part of pyserial (http://pyserial.sf.net)  (C)2002 cliechti@gmx.net

Intended to be run on different platforms, to ensure portability of
the code.

These tests open a serial port and change all the settings on the fly.
If the port is really correctly configured cannot be determined - that
would require external hardware or a null modem cable and an other
serial port library... Thus it mainly tests that all features are
correctly implemented and that the interface does what it should.

"""

import unittest
import serial

# on which port should the tests be performed:
PORT = 'loop://'


class Test_ChangeAttributes(unittest.TestCase):
    """Test with timeouts"""

    def setUp(self):
        # create a closed serial port
        self.s = serial.serial_for_url(PORT, do_not_open=True)

    def tearDown(self):
        self.s.close()

    def test_PortSetting(self):
        self.s.port = PORT
        self.assertEqual(self.s.portstr.lower(), PORT.lower())
        # test internals
        self.assertEqual(self.s._port, PORT)
        # test on the fly change
        self.s.open()
        self.assertTrue(self.s.isOpen())

    def test_DoubleOpen(self):
        self.s.open()
        # calling open for a second time is an error
        self.assertRaises(serial.SerialException, self.s.open)

    def test_BaudrateSetting(self):
        self.s.open()
        for baudrate in (300, 9600, 19200, 115200):
            self.s.baudrate = baudrate
            # test get method
            self.assertEqual(self.s.baudrate, baudrate)
            # test internals
            self.assertEqual(self.s._baudrate, baudrate)
        # test illegal values
        for illegal_value in (-300, -1, 'a', None):
            self.assertRaises(ValueError, setattr, self.s, 'baudrate', illegal_value)

    # skip this test as pyserial now tries to set even non standard baud rates.
    # therefore the test can not choose a value that fails on any system.
    def disabled_test_BaudrateSetting2(self):
        # test illegal values, depending on machine/port some of these may be valid...
        self.s.open()
        for illegal_value in (500000, 576000, 921600, 92160):
            self.assertRaises(ValueError, setattr, self.s, 'baudrate', illegal_value)

    def test_BytesizeSetting(self):
        for bytesize in (5, 6, 7, 8):
            self.s.bytesize = bytesize
            # test get method
            self.assertEqual(self.s.bytesize, bytesize)
            # test internals
            self.assertEqual(self.s._bytesize, bytesize)
        # test illegal values
        for illegal_value in (0, 1, 3, 4, 9, 10, 'a', None):
            self.assertRaises(ValueError, setattr, self.s, 'bytesize', illegal_value)

    def test_ParitySetting(self):
        for parity in (serial.PARITY_NONE, serial.PARITY_EVEN, serial.PARITY_ODD):
            self.s.parity = parity
            # test get method
            self.assertEqual(self.s.parity, parity)
            # test internals
            self.assertEqual(self.s._parity, parity)
        # test illegal values
        for illegal_value in (0, 57, 'a', None):
            self.assertRaises(ValueError, setattr, self.s, 'parity', illegal_value)

    def test_StopbitsSetting(self):
        for stopbits in (1, 2):
            self.s.stopbits = stopbits
            # test get method
            self.assertEqual(self.s.stopbits, stopbits)
            # test internals
            self.assertEqual(self.s._stopbits, stopbits)
        # test illegal values
        for illegal_value in (0, 3, 2.5, 57, 'a', None):
            self.assertRaises(ValueError, setattr, self.s, 'stopbits', illegal_value)

    def test_TimeoutSetting(self):
        for timeout in (None, 0, 1, 3.14159, 10, 1000, 3600):
            self.s.timeout = timeout
            # test get method
            self.assertEqual(self.s.timeout, timeout)
            # test internals
            self.assertEqual(self.s._timeout, timeout)
        # test illegal values
        for illegal_value in (-1, 'a'):
            self.assertRaises(ValueError, setattr, self.s, 'timeout', illegal_value)

    def test_XonXoffSetting(self):
        for xonxoff in (True, False):
            self.s.xonxoff = xonxoff
            # test get method
            self.assertEqual(self.s.xonxoff, xonxoff)
            # test internals
            self.assertEqual(self.s._xonxoff, xonxoff)
        # no illegal values here, normal rules for the boolean value of an
        # object are used thus all objects have a truth value.

    def test_RtsCtsSetting(self):
        for rtscts in (True, False):
            self.s.rtscts = rtscts
            # test get method
            self.assertEqual(self.s.rtscts, rtscts)
            # test internals
            self.assertEqual(self.s._rtscts, rtscts)
        # no illegal values here, normal rules for the boolean value of an
        # object are used thus all objects have a truth value.

    # this test does not work anymore since serial_for_url that is used
    # now, already sets a port
    def disabled_test_UnconfiguredPort(self):
        # an unconfigured port cannot be opened
        self.assertRaises(serial.SerialException, self.s.open)

    def test_PortOpenClose(self):
        for i in range(3):
            # open the port and check flag
            self.assertTrue(not self.s.isOpen())
            self.s.open()
            self.assertTrue(self.s.isOpen())
            self.s.close()
            self.assertTrue(not self.s.isOpen())


if __name__ == '__main__':
    import sys
    sys.stdout.write(__doc__)
    if len(sys.argv) > 1:
        PORT = sys.argv[1]
    sys.stdout.write("Testing port: {!r}\n".format(PORT))
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
