#!/usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Test RS485 related functionality.
"""

import errno
import os
import sys
import unittest
from unittest import mock

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


@unittest.skipUnless(hasattr(os, 'openpty'), 'requires a POSIX pseudo-terminal')
class Test_RS485_posix_reset(unittest.TestCase):
    def test_explicit_reset_reaches_linux_driver_only(self):
        import serial.serialposix

        master, slave = os.openpty()
        try:
            with mock.patch.object(serial.Serial, '_set_rs485_mode') as update:
                port = serial.Serial(os.ttyname(slave))
                try:
                    update.assert_not_called()  # opening a normal port needs no RS485 ioctl
                    with mock.patch.object(serial.serialposix, 'plat', 'linux'):
                        port.rs485_mode = None
                    update.assert_called_once_with(None)
                    port.timeout = 1
                    update.assert_called_once_with(None)
                finally:
                    port.close()
        finally:
            os.close(master)
            os.close(slave)


@unittest.skipUnless(sys.platform.startswith('linux'), 'requires Linux RS485 ioctls')
class Test_RS485_linux_ioctl(unittest.TestCase):
    def test_reset_clears_enabled_flag(self):
        from serial import serialposix

        port = serial.Serial(port=None)
        port.fd = 123
        observed = []

        def ioctl(fd, request, buf):
            self.assertEqual(fd, 123)
            observed.append(request)
            if request == serialposix.TIOCGRS485:
                buf[0] = serialposix.SER_RS485_ENABLED
            else:
                self.assertEqual(request, serialposix.TIOCSRS485)
                self.assertEqual(buf[0], 0)

        with mock.patch.object(serialposix.fcntl, 'ioctl', side_effect=ioctl):
            port._set_rs485_mode(None)
        self.assertEqual(observed, [serialposix.TIOCGRS485,
                                    serialposix.TIOCSRS485])

    def test_reset_ignores_unsupported_ioctl_but_enable_does_not(self):
        from serial import serialposix

        port = serial.Serial(port=None)
        port.fd = 123
        with mock.patch.object(serialposix.fcntl, 'ioctl',
                               side_effect=OSError(errno.ENOTTY, 'not supported')):
            port._set_rs485_mode(None)
            with self.assertRaisesRegex(ValueError, 'Failed to set RS485 mode'):
                port._set_rs485_mode(serial.rs485.RS485Settings())


if __name__ == '__main__':
    import sys
    sys.stdout.write(__doc__)
    if len(sys.argv) > 1:
        PORT = sys.argv[1]
    sys.stdout.write("Testing port: {!r}\n".format(PORT))
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
