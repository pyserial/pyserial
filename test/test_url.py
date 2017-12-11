#! /usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2001-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Some tests for the serial module.
Part of pySerial (http://pyserial.sf.net)  (C)2001-2011 cliechti@gmx.net

Intended to be run on different platforms, to ensure portability of
the code.

Cover some of the aspects of serial_for_url and the extension mechanism.
"""

import os
import unittest
import serial
import sys


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

    def test_fully_qualified_custom_url(self):
        """custom protocol handlers with fully qualified names"""
        old_path = list(sys.path)
        try:
            # For serial_for_url('handlers.test://') to work, sys.path needs
            # to include the parent of the top-level package; handlers is that
            # package in this case, and this test's directory is the parent of
            # that package.
            this_dir = os.path.dirname(os.path.abspath(__file__))

            # Make sure that sys.path does not include this_dir. Start by making the path
            # absolute.
            sys.path = [os.path.abspath(v) for v in sys.path]
            sys.path = [v for v in sys.path if not v == this_dir]

            # Because of the other tests, the module will already be imported, so remove it.
            if 'handlers' in sys.modules:
                del sys.modules['handlers']
            if 'handlers.test' in sys.modules:
                del sys.modules['handlers.test']

            # It's unknown because sys.path doesn't include this_dir.
            self.assertRaises(ValueError, serial.serial_for_url, "handlers.test://")

            # Add this_dir to sys.path.
            sys.path.insert(0, this_dir)

            # now it should work
            serial.serial_for_url("handlers.test://")
        finally:
            sys.path = old_path


if __name__ == '__main__':
    import sys
    sys.stdout.write(__doc__)
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
