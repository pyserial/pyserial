#!/usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""
Test cancel functionality.
"""
import sys
import unittest
import threading
import time
import serial

# on which port should the tests be performed:
PORT = 'loop://'


@unittest.skipIf(not hasattr(serial.Serial, 'cancel_read'), "cancel_read not supported on platform")
class TestCancelRead(unittest.TestCase):
    """Test cancel_read functionality"""

    def setUp(self):
        # create a closed serial port
        self.s = serial.serial_for_url(PORT)
        self.assertTrue(hasattr(self.s, 'cancel_read'), "serial instance has no cancel_read")
        self.s.timeout = 10
        self.cancel_called = 0

    def tearDown(self):
        self.s.reset_output_buffer()
        self.s.close()

    def _cancel(self, num_times):
        for i in range(num_times):
            #~ print "cancel"
            self.cancel_called += 1
            self.s.cancel_read()

    def test_cancel_once(self):
        """Cancel read"""
        threading.Timer(1, self._cancel, ((1,))).start()
        t1 = time.time()
        self.s.read(1000)
        t2 = time.time()
        self.assertEqual(self.cancel_called, 1)
        self.assertTrue(0.5 < (t2 - t1) < 2, 'Function did not return in time: {}'.format(t2 - t1))
        #~ self.assertTrue(not self.s.isOpen())
        #~ self.assertRaises(serial.SerialException, self.s.open)

    #~ def test_cancel_before_read(self):
        #~ self.s.cancel_read()
        #~ self.s.read()


DATA = b'#' * 1024


@unittest.skipIf(not hasattr(serial.Serial, 'cancel_write'), "cancel_read not supported on platform")
class TestCancelWrite(unittest.TestCase):
    """Test cancel_write functionality"""

    def setUp(self):
        # create a closed serial port
        self.s = serial.serial_for_url(PORT, baudrate=300)  # extra slow ~30B/s => 1kb ~ 34s
        self.assertTrue(hasattr(self.s, 'cancel_write'), "serial instance has no cancel_write")
        self.s.write_timeout = 10
        self.cancel_called = 0

    def tearDown(self):
        self.s.reset_output_buffer()
        # not all USB-Serial adapters will actually flush the output (maybe
        # keeping the buffer in the MCU in the adapter) therefore, speed up by
        # changing the baudrate
        self.s.baudrate = 115200
        self.s.flush()
        self.s.close()

    def _cancel(self, num_times):
        for i in range(num_times):
            self.cancel_called += 1
            self.s.cancel_write()

    def test_cancel_once(self):
        """Cancel write"""
        threading.Timer(1, self._cancel, ((1,))).start()
        t1 = time.time()
        self.s.write(DATA)
        t2 = time.time()
        self.assertEqual(self.cancel_called, 1)
        self.assertTrue(0.5 < (t2 - t1) < 2, 'Function did not return in time: {}'.format(t2 - t1))
        #~ self.assertTrue(not self.s.isOpen())
        #~ self.assertRaises(serial.SerialException, self.s.open)

    #~ def test_cancel_before_write(self):
        #~ self.s.cancel_write()
        #~ self.s.write(DATA)
        #~ self.s.reset_output_buffer()


if __name__ == '__main__':
    sys.stdout.write(__doc__)
    if len(sys.argv) > 1:
        PORT = sys.argv[1]
    sys.stdout.write("Testing port: {!r}\n".format(PORT))
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
