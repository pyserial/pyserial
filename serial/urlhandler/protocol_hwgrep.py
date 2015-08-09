#! python
#
# Python Serial Port Extension for Win32, Linux, BSD, Jython
# see __init__.py
#
# This module implements a special URL handler that uses the port listing to
# find ports by searching the string descriptions.
#
# (C) 2011-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
# URL format:    hwgrep://regexp

import serial
import serial.tools.list_ports

try:
    basestring
except NameError:
    basestring = str    # python 3

class Serial(serial.Serial):
    """Just inherit the native Serial port implementation and patch the port property."""

    @serial.Serial.port.setter
    def port(self, value):
        """translate port name before storing it"""
        if isinstance(value, basestring) and value.startswith('hwgrep://'):
            serial.Serial.port.__set__(self, self.fromURL(value))
        else:
            serial.Serial.port.__set__(self, value)

    def fromURL(self, url):
        """extract host and port from an URL string"""
        if url.lower().startswith("hwgrep://"):
            url = url[9:]
        # use a for loop to get the 1st element from the generator
        for port, desc, hwid in serial.tools.list_ports.grep(url):
            return port
        else:
            raise serial.SerialException('no ports found matching regexp %r' % (url,))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    #~ s = Serial('hwgrep://ttyS0')
    s = Serial(None)
    s.port = 'hwgrep://ttyS0'
    print(s)

