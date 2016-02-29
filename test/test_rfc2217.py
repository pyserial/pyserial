#! /usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Test RFC 2217 related functionality.
"""

import unittest
import serial
import serial.rfc2217


class Test_RFC2217(unittest.TestCase):
    """Test RFC 2217 related functionality"""

    def test_failed_connection(self):
        # connection to closed port
        s = serial.serial_for_url('rfc2217://127.99.99.99:2217', do_not_open=True)
        self.assertRaises(serial.SerialException, s.open)
        self.assertFalse(s.is_open)
        s.close()  # no errors expected
        # invalid address
        s = serial.serial_for_url('rfc2217://127goingtofail', do_not_open=True)
        self.assertRaises(serial.SerialException, s.open)
        self.assertFalse(s.is_open)
        s.close()  # no errors expected
        # close w/o open is also OK
        s = serial.serial_for_url('rfc2217://irrelevant', do_not_open=True)
        self.assertFalse(s.is_open)
        s.close()  # no errors expected


if __name__ == '__main__':
    import sys
    sys.stdout.write(__doc__)
    sys.stdout.write("Testing connection on localhost\n")
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
