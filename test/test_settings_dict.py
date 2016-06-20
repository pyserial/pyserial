#!/usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2002-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Test the ability to get and set the settings with a dictionary.

Part of pySerial (http://pyserial.sf.net)  (C) 2002-2015 cliechti@gmx.net

"""

import unittest
import serial

# on which port should the tests be performed:
PORT = 0


SETTINGS = ('baudrate', 'bytesize', 'parity', 'stopbits', 'xonxoff',
            'dsrdtr', 'rtscts', 'timeout', 'write_timeout', 'inter_byte_timeout')


class Test_SettingsDict(unittest.TestCase):
    """Test with settings dictionary"""

    def test_getsettings(self):
        """the settings dict reflects the current settings"""
        ser = serial.serial_for_url(PORT, do_not_open=True)
        d = ser.get_settings()
        for setting in SETTINGS:
            self.assertEqual(getattr(ser, setting), d[setting])

    def test_partial_settings(self):
        """partial settings dictionaries are also accepted"""
        ser = serial.serial_for_url(PORT, do_not_open=True)
        d = ser.get_settings()
        del d['baudrate']
        del d['bytesize']
        ser.apply_settings(d)
        for setting in d:
            self.assertEqual(getattr(ser, setting), d[setting])

    def test_unknown_settings(self):
        """unknown settings are ignored"""
        ser = serial.serial_for_url(PORT, do_not_open=True)
        d = ser.get_settings()
        d['foobar'] = 'ignore me'
        ser.apply_settings(d)

    def test_init_sets_the_correct_attrs(self):
        """__init__ sets the fields that get_settings reads"""
        for setting, value in (
                ('baudrate', 57600),
                ('timeout', 7),
                ('write_timeout', 12),
                ('inter_byte_timeout', 15),
                ('stopbits', serial.STOPBITS_TWO),
                ('bytesize', serial.SEVENBITS),
                ('parity', serial.PARITY_ODD),
                ('xonxoff', True),
                ('rtscts', True),
                ('dsrdtr', True)):
            kwargs = {'do_not_open': True, setting: value}
            ser = serial.serial_for_url(PORT, **kwargs)
            d = ser.get_settings()
            self.assertEqual(getattr(ser, setting), value)
            self.assertEqual(d[setting], value)


if __name__ == '__main__':
    import sys
    sys.stdout.write(__doc__)
    if len(sys.argv) > 1:
        PORT = sys.argv[1]
    sys.stdout.write("Testing port: {!r}\n".format(PORT))
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
