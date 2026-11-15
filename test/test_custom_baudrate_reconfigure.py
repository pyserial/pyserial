#!/usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
#
# SPDX-License-Identifier:    BSD-3-Clause
"""
Reconfiguring an open POSIX port must not disturb the line:
- changing ``timeout`` does not reconfigure (the timeout is done with select()),
- a reconfigure at a custom baud rate the port already uses does not switch the
  line to the B38400 placeholder and back (macOS reports the numeric rate),
- a VMIN/VTIME-only change (inter_byte_timeout) is still applied,
- on Linux a custom rate is set in one call, never via the B38400 placeholder.
"""

import os
import sys
import unittest
from unittest import mock

try:
    import pty
    import termios
    import serial.serialposix as serialposix
except ImportError:
    pty = termios = serialposix = None

import serial

CUSTOM = 10400  # not a standard termios rate (automotive K-line)


@unittest.skipIf(pty is None or serialposix is None, "needs pty and the POSIX implementation")
class Test_TimeoutDoesNotReconfigure(unittest.TestCase):

    def setUp(self):
        self.master, self.slave = pty.openpty()

    def tearDown(self):
        os.close(self.master)
        os.close(self.slave)

    def test_timeout_change_skips_reconfigure(self):
        with serialposix.Serial(os.ttyname(self.slave), 9600) as ser:
            with mock.patch.object(ser, "_reconfigure_port") as reconfigure:
                ser.timeout = 0.25
                ser.timeout = None
                ser.write_timeout = 1
            reconfigure.assert_not_called()
            self.assertIsNone(ser.timeout)
            self.assertEqual(ser.write_timeout, 1)

    def test_inter_byte_timeout_reaches_termios(self):
        with serialposix.Serial(os.ttyname(self.slave), 9600) as ser:
            ser.inter_byte_timeout = 0.3
            cc = termios.tcgetattr(ser.fd)[6]
            self.assertEqual((cc[termios.VMIN], cc[termios.VTIME]), (1, 3))
            ser.inter_byte_timeout = None
            cc = termios.tcgetattr(ser.fd)[6]
            self.assertEqual((cc[termios.VMIN], cc[termios.VTIME]), (0, 0))

    def test_invalid_timeout_still_rejected(self):
        with serialposix.Serial(os.ttyname(self.slave), 9600) as ser:
            with self.assertRaises(ValueError):
                ser.timeout = -1

    def test_vtime_serial_still_reconfigures(self):
        with serialposix.VTIMESerial(os.ttyname(self.slave), 9600) as ser:
            with mock.patch.object(ser, "_reconfigure_port") as reconfigure:
                ser.timeout = 0.5
            reconfigure.assert_called_once()

    def test_vtime_serial_writes_settings_once(self):
        with serialposix.VTIMESerial(os.ttyname(self.slave), 9600, timeout=1) as ser:
            with mock.patch("serial.serialposix.termios.tcsetattr",
                            wraps=termios.tcsetattr) as tcsetattr:
                ser.timeout = 0.5
            self.assertEqual(tcsetattr.call_count, 1)
            cc = termios.tcgetattr(ser.fd)[6]
            self.assertEqual((cc[termios.VMIN], cc[termios.VTIME]), (0, 5))

    def test_other_settings_still_reconfigure(self):
        with serialposix.Serial(os.ttyname(self.slave), 9600) as ser:
            with mock.patch.object(ser, "_reconfigure_port") as reconfigure:
                ser.inter_byte_timeout = 0.1
                ser.parity = serial.PARITY_EVEN
            self.assertEqual(reconfigure.call_count, 2)


@unittest.skipIf(pty is None or termios is None, "needs pty and termios")
@unittest.skipIf(sys.platform != "darwin", "custom rates via IOSSIOSPEED are macOS only")
class Test_CustomBaudrateReconfigure(unittest.TestCase):

    def setUp(self):
        self.master, self.slave = pty.openpty()
        self.ser = serial.Serial(os.ttyname(self.slave), 9600)
        # A pty cannot take IOSSIOSPEED; record the call instead and pretend the kernel
        # now reports the custom rate, as a real macOS serial driver does.
        self.special = []
        self.ser._set_special_baudrate = self.special.append
        self.reported = [CUSTOM]
        real_get = termios.tcgetattr

        def tcgetattr(fd):
            attrs = real_get(fd)
            attrs[4] = attrs[5] = self.reported[0]
            return attrs

        self.tcsetattr = mock.patch("serial.serialposix.termios.tcsetattr").start()
        mock.patch("serial.serialposix.termios.tcgetattr", side_effect=tcgetattr).start()
        self.addCleanup(mock.patch.stopall)
        self.ser._baudrate = CUSTOM  # as after `ser.baudrate = 10400`

    def tearDown(self):
        mock.patch.stopall()
        self.ser.close()
        os.close(self.master)
        os.close(self.slave)

    def test_reconfigure_at_current_custom_rate_touches_nothing(self):
        for _ in range(3):
            self.ser._reconfigure_port()
        self.tcsetattr.assert_not_called()
        self.assertEqual(self.special, [])

    def test_rate_change_still_applied(self):
        self.reported[0] = 9600  # kernel at another rate: must switch
        self.ser._reconfigure_port()
        self.assertEqual(self.special, [CUSTOM])

    def test_other_setting_change_still_applied(self):
        self.ser.parity = serial.PARITY_EVEN
        self.tcsetattr.assert_called()
        self.assertEqual(self.special, [CUSTOM])

    def test_vmin_vtime_change_still_applied(self):
        self.ser.inter_byte_timeout = 0.3
        self.tcsetattr.assert_called_once()
        attrs = self.tcsetattr.call_args[0][2]
        self.assertEqual(attrs[4:6], [termios.B38400, termios.B38400])  # placeholder, then IOSSIOSPEED
        self.assertEqual((attrs[6][termios.VMIN], attrs[6][termios.VTIME]), (1, 3))
        self.assertEqual(self.special, [CUSTOM])

    def test_forced_update_still_applied(self):
        self.ser._reconfigure_port(force_update=True)
        self.tcsetattr.assert_called()
        self.assertEqual(self.special, [CUSTOM])



LINUX = sys.platform.startswith("linux") and serialposix is not None


@unittest.skipIf(not LINUX or pty is None, "Linux only")
@unittest.skipIf(LINUX and not serialposix.TCSETATTR_ANY_RATE
                 and not hasattr(serialposix.Serial, "_set_attrs_custom_baudrate"),
                 "custom rates still use the placeholder on this architecture")
class Test_LinuxCustomBaudrate(unittest.TestCase):
    """At a custom rate, Linux must never pass through the B38400 placeholder."""

    def setUp(self):
        self.master, self.slave = pty.openpty()
        self.ser = serialposix.Serial(os.ttyname(self.slave), CUSTOM)
        self.calls = []
        real_set, real_ioctl = termios.tcsetattr, serialposix.fcntl.ioctl

        def tcsetattr(fd, when, attrs):
            self.calls.append(("tcsetattr", attrs[4]))
            return real_set(fd, when, attrs)

        def ioctl(fd, request, *args):
            if request == serialposix.TCSETS2:
                self.calls.append(("TCSETS2", None))
            return real_ioctl(fd, request, *args)

        self._real_ioctl = real_ioctl
        mock.patch("serial.serialposix.termios.tcsetattr", side_effect=tcsetattr).start()
        mock.patch("serial.serialposix.fcntl.ioctl", side_effect=ioctl).start()
        self.addCleanup(mock.patch.stopall)

    def tearDown(self):
        mock.patch.stopall()
        self.ser.close()
        os.close(self.master)
        os.close(self.slave)

    def kernel_rate(self):
        import array
        buf = array.array('i', [0] * 64)
        self._real_ioctl(self.ser.fd, serialposix.TCGETS2, buf)
        offset = serialposix.BAUDRATE_OFFSET
        return buf[offset], buf[offset + 1]

    def assert_no_placeholder(self):
        placeholder = 38400 if serialposix.TCSETATTR_ANY_RATE else termios.B38400
        self.assertNotIn(("tcsetattr", placeholder), self.calls)

    def test_open_sets_custom_rate(self):
        self.assertEqual(self.kernel_rate(), (CUSTOM, CUSTOM))

    def test_unchanged_reconfigure_touches_nothing(self):
        self.ser._reconfigure_port()
        self.assertEqual(self.calls, [])

    def test_setting_change_is_one_call_at_the_custom_rate(self):
        self.ser.stopbits = serial.STOPBITS_TWO
        self.assertEqual(len(self.calls), 1)
        self.assert_no_placeholder()
        self.assertTrue(termios.tcgetattr(self.ser.fd)[2] & termios.CSTOPB)
        self.assertEqual(self.kernel_rate(), (CUSTOM, CUSTOM))

    def test_inter_byte_timeout_applied_at_custom_rate(self):
        self.ser.inter_byte_timeout = 0.2
        self.assert_no_placeholder()
        cc = termios.tcgetattr(self.ser.fd)[6]
        self.assertEqual((cc[termios.VMIN], cc[termios.VTIME]), (1, 2))
        self.assertEqual(self.kernel_rate(), (CUSTOM, CUSTOM))

    def test_switch_from_standard_to_custom_rate(self):
        self.ser.baudrate = 9600
        self.calls.clear()
        self.ser.baudrate = CUSTOM
        self.assertEqual(len(self.calls), 1)
        self.assert_no_placeholder()
        self.assertEqual(self.kernel_rate(), (CUSTOM, CUSTOM))



@unittest.skipIf(sys.platform != "win32", "Windows only")
class Test_Win32ReconfigureKeepsCommState(unittest.TestCase):
    """A timeout change must not call SetCommState(): the driver reprograms the UART."""

    def setUp(self):
        import ctypes
        import serial.serialwin32 as serialwin32

        self.ser = serialwin32.Serial()
        self.ser._port_handle = 1  # never used: all win32 calls are mocked
        self.ser.is_open = True
        self.state = {}

        def get_comm_state(handle, dcb_ref):
            dcb = dcb_ref._obj
            if "dcb" in self.state:
                ctypes.memmove(ctypes.addressof(dcb), self.state["dcb"], ctypes.sizeof(dcb))
            return 1

        def set_comm_state(handle, dcb_ref):
            self.state["dcb"] = bytes(dcb_ref._obj)
            return 1

        win32 = serialwin32.win32
        self.set_comm_state = mock.Mock(side_effect=set_comm_state)
        self.set_comm_mask = mock.Mock(return_value=1)
        self.set_comm_timeouts = mock.Mock(return_value=1)
        for name, value in (("GetCommState", get_comm_state), ("SetCommState", self.set_comm_state),
                            ("SetCommMask", self.set_comm_mask),
                            ("SetCommTimeouts", self.set_comm_timeouts)):
            patcher = mock.patch.object(win32, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.ser._reconfigure_port(force_update=True)
        for m in (self.set_comm_state, self.set_comm_mask, self.set_comm_timeouts):
            m.reset_mock()

    def tearDown(self):
        self.ser.is_open = False
        self.ser._port_handle = None

    def test_timeout_change_only_sets_timeouts(self):
        self.ser.timeout = 0.5
        self.ser.write_timeout = 1
        self.set_comm_state.assert_not_called()
        self.set_comm_mask.assert_not_called()
        self.assertEqual(self.set_comm_timeouts.call_count, 2)

    def test_real_change_still_sets_comm_state(self):
        self.ser.parity = serial.PARITY_EVEN
        self.set_comm_state.assert_called_once()


if __name__ == '__main__':
    sys.stdout.write(__doc__)
    unittest.main()
