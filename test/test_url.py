#! /usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2001-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Some tests for the serial module.
Part of pySerial (https://github.com/pyserial/pyserial)  (C)2001-2011 cliechti@gmx.net

Intended to be run on different platforms, to ensure portability of
the code.

Cover some of the aspects of serial_for_url and the extension mechanism.
"""

import unittest
import serial


class Test_URL(unittest.TestCase):
    """Test serial_for_url"""

    def test_loop(self):
        """loop interface"""
        serial.serial_for_url('loop://', do_not_open=True)

    def test_bad_url(self):
        """invalid protocol specified"""
        self.assertRaises(ValueError, serial.serial_for_url, "imnotknown://")

    def test_custom_url(self):
        """custom protocol handlers"""
        # it's unknown
        self.assertRaises(ValueError, serial.serial_for_url, "test://")
        # add search path
        serial.protocol_handler_packages.append('handlers')
        # now it should work
        serial.serial_for_url("test://")
        # remove our handler again
        serial.protocol_handler_packages.remove('handlers')
        # so it should not work anymore
        self.assertRaises(ValueError, serial.serial_for_url, "test://")


    def test_socket_connect_timeout(self):
        """socket URL connect timeout option"""
        port = serial.serial_for_url(
            'socket://localhost:7000?connect_timeout=0.5',
            do_not_open=True)
        port.from_url(port.port)
        self.assertEqual(port._connect_timeout, 0.5)

        default_port = serial.serial_for_url(
            'socket://localhost:7000',
            do_not_open=True)
        default_port.from_url(default_port.port)
        self.assertEqual(default_port._connect_timeout, 5)

        for value in ('0', '-1', 'nan', 'inf', '-inf', 'abc', ''):
            port = serial.serial_for_url(
                'socket://localhost:7000?connect_timeout={}'.format(value),
                do_not_open=True)
            self.assertRaises(serial.SerialException, port.from_url, port.port)

        # Reusing a port without the option must restore the default.
        port.from_url('socket://localhost:7000?connect_timeout=1.25')
        self.assertEqual(port._connect_timeout, 1.25)
        port.from_url('socket://localhost:7000')
        self.assertEqual(port._connect_timeout, 5)

    def test_socket_connect_timeout_used_by_open(self):
        """The URL setting must reach the actual socket connection attempt."""
        from serial.urlhandler import protocol_socket

        port = serial.serial_for_url(
            'socket://localhost:7000?connect_timeout=0.5',
            do_not_open=True)
        calls = []
        original_create_connection = protocol_socket.socket.create_connection

        def capture_connection(address, timeout):
            calls.append((address, timeout))
            raise OSError('simulated connection failure')

        try:
            protocol_socket.socket.create_connection = capture_connection
            self.assertRaises(serial.SerialException, port.open)
        finally:
            protocol_socket.socket.create_connection = original_create_connection

        self.assertEqual(calls, [(('localhost', 7000), 0.5)])


if __name__ == '__main__':
    import sys
    sys.stdout.write(__doc__)
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
