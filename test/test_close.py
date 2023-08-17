#! /usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2001-2015 Chris Liechti <cliechti@gmx.net>
# (C) 2023 Google LLC
#
# SPDX-License-Identifier:    BSD-3-Clause
import sys
import unittest
import serial

# on which port should the tests be performed:
PORT = 'loop://'

class TestClose(unittest.TestCase):

    def test_closed_true(self):
        # closed is True if a Serial port is not open
        s = serial.Serial()
        self.assertFalse(s.is_open)
        self.assertTrue(s.closed)

    def test_closed_false(self):
        # closed is False if a Serial port is open
        s = serial.serial_for_url(PORT, timeout=1)
        self.assertTrue(s.is_open)
        self.assertFalse(s.closed)

        s.close()
        self.assertTrue(s.closed)

    def test_close_not_called_by_finalize_if_closed(self):
        close_calls = 0

        class TestSerial(serial.Serial):
            def close(self):
                nonlocal close_calls
                close_calls += 1

        with TestSerial() as s:
            pass
            # close() should be called here

        # Trigger RawIOBase finalization.
        # Because we override .closed, close() should not be called
        # if Serial says it is already closed.
        del s

        self.assertEqual(close_calls, 1)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    if len(sys.argv) > 1:
        PORT = sys.argv[1]
    sys.stdout.write("Testing port: {!r}\n".format(PORT))
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
