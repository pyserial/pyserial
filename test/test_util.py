#!/usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Tests for utility functions of serualutil.
"""

import os
import pickle
import unittest
import serial


class Test_util(unittest.TestCase):
    """Test serial utility functions"""

    def test_to_bytes(self):
        self.assertEqual(serial.to_bytes([1, 2, 3]), b'\x01\x02\x03')
        self.assertEqual(serial.to_bytes(b'\x01\x02\x03'), b'\x01\x02\x03')
        self.assertEqual(serial.to_bytes(bytearray([1,2,3])), b'\x01\x02\x03')
        # unicode is not supported test. use decode() instead of u'' syntax to be
        # compatible to Python 3.x < 3.4
        self.assertRaises(TypeError, serial.to_bytes, b'hello'.decode('utf-8'))

    def test_iterbytes(self):
        self.assertEqual(list(serial.iterbytes(b'\x01\x02\x03')), [b'\x01', b'\x02', b'\x03'])


class TestSerialExceptions(unittest.TestCase):
    def test_port_not_open_error_default_message(self):
        error = serial.PortNotOpenError()
        self.assertEqual(str(error), 'Attempting to use a port that is not open')

    def test_closed_port_error_pickle(self):
        port = serial.serial_for_url('loop://', do_not_open=True)
        with self.assertRaises(serial.PortNotOpenError) as caught:
            port.read(1)
        error = caught.exception
        error.operation = 'read'
        for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
            with self.subTest(protocol=protocol):
                restored = pickle.loads(pickle.dumps(error, protocol))
                self.assertIs(type(restored), serial.PortNotOpenError)
                self.assertEqual(restored.args, error.args)
                self.assertEqual(str(restored), str(error))
                self.assertEqual(restored.operation, 'read')

    def test_serial_exception_arguments_pickle(self):
        for exception in (serial.SerialException, serial.SerialTimeoutException,
                          serial.PortNotOpenError):
            for args in [('custom message',), (5, 'I/O error', 'port')]:
                for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
                    with self.subTest(exception=exception, args=args, protocol=protocol):
                        error = exception(*args)
                        restored = pickle.loads(pickle.dumps(error, protocol))
                        self.assertIs(type(restored), exception)
                        self.assertEqual(restored.args, error.args)
                        self.assertEqual(str(restored), str(error))
                        self.assertEqual(restored.errno, error.errno)
                        self.assertEqual(restored.strerror, error.strerror)
                        self.assertEqual(restored.filename, error.filename)


if __name__ == '__main__':
    import sys
    sys.stdout.write(__doc__)
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
