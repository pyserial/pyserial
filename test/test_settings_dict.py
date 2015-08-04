#!/usr/bin/env python

# Python Serial Port Extension for Win32, Linux, BSD, Jython
# see __init__.py
#
# (C) 2015 Chris Liechti <cliechti@gmx.net>
# this is distributed under a free software license, see license.txt

"""\
Test the ability to get and set the settings with a dictionary.

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
PORT = 0


SETTINGS = ('baudrate', 'bytesize', 'parity', 'stopbits', 'xonxoff',
            'dsrdtr', 'rtscts', 'timeout', 'writeTimeout', 'interCharTimeout')


class Test_SettingsDict(unittest.TestCase):
    """Test with ettings dictionary"""

    def setUp(self):
        # create a closed serial port
        self.s = serial.serial_for_url(PORT, do_not_open=True)

    def tearDown(self):
        self.s.close()

    def test_getsettings(self):
        """the settings dict reflects the current settings"""
        d = self.s.getSettingsDict()
        for setting in SETTINGS:
            self.failUnlessEqual(getattr(self.s, setting), d[setting])

    def test_partial_settings(self):
        """partial settings dictionaries are also accepted"""
        d = self.s.getSettingsDict()
        del d['baudrate']
        del d['bytesize']
        self.s.applySettingsDict(d)
        for setting in d:
            self.failUnlessEqual(getattr(self.s, setting), d[setting])

    def test_unknown_settings(self):
        """unknown settings are ignored"""
        d = self.s.getSettingsDict()
        d['foobar'] = 'ignore me'
        self.s.applySettingsDict(d)


if __name__ == '__main__':
    import sys
    sys.stdout.write(__doc__)
    if len(sys.argv) > 1:
        PORT = sys.argv[1]
    sys.stdout.write("Testing port: %r\n" % PORT)
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
