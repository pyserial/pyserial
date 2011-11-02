#! /usr/bin/env python
# Python Serial Port Extension for Win32, Linux, BSD, Jython
# see __init__.py
#
# (C) 2001-2008 Chris Liechti <cliechti@gmx.net>
# this is distributed under a free software license, see license.txt

"""\
Some tests for the serial module.
Part of pySerial (http://pyserial.sf.net)  (C)2001-2011 cliechti@gmx.net

Intended to be run on different platforms, to ensure portability of
the code.

Cover some of the aspects of serial_for_url and the extension mechanism.
"""

import unittest
import time
import sys
import serial


class Test_URL(unittest.TestCase):
    """Test serial_for_url"""

    def test_loop(self):
        """loop interface"""
        s = serial.serial_for_url('loop://', do_not_open=True)

    def test_bad_url(self):
        """invalid protocol specified"""
        self.failUnlessRaises(ValueError, serial.serial_for_url, "imnotknown://")

    def test_custom_url(self):
        """custom protocol handlers"""
        # it's unknown
        self.failUnlessRaises(ValueError, serial.serial_for_url, "test://")
        # add search path
        serial.protocol_handler_packages.append('handlers')
        # now it should work
        s = serial.serial_for_url("test://")
        # remove our handler again
        serial.protocol_handler_packages.remove('handlers')
        # so it should not work anymore
        self.failUnlessRaises(ValueError, serial.serial_for_url, "test://")


if __name__ == '__main__':
    import sys
    sys.stdout.write(__doc__)
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
