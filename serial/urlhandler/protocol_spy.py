#! python
#
# Python Serial Port Extension for Win32, Linux, BSD, Jython
# see __init__.py
#
# This module implements a special URL handler that wraps an other port,
# printint the traffic for debugging purposes
#
# (C) 2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
# URL format:    spy://port[?option[=value][&option[=value]]]
# options:
# - dev=X   a file or device to write to
# - color   use escape code to colorize output
# - hex     hex encode the output
#
# example:
#   redirect output to an other terminal window on Posix (Linux):
#   python -m serial.tools.miniterm spy:///dev/ttyUSB0?dev=/dev/pts/12\&color

import sys
import serial

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse
try:
    basestring
except NameError:
    basestring = str    # python 3

class Serial(serial.Serial):
    """Just inherit the native Serial port implementation and patch the port property."""

    def __init__(self, *args, **kwargs):
        super(Serial, self).__init__(*args, **kwargs)
        self.output = sys.stderr
        self.hexlify = False
        self.color = False
        self.rx_color = '\x1b[32m'
        self.tx_color = '\x1b[31m'

    @serial.Serial.port.setter
    def port(self, value):
        if value is not None:
            serial.Serial.port.__set__(self, self.fromURL(value))

    def fromURL(self, url):
        """extract host and port from an URL string"""
        print(url)
        parts = urlparse.urlsplit(url)
        if parts.scheme != "spy":
            raise serial.SerialException('expected a string in the form "spy://port[?option[=value][&option[=value]]]": not starting with spy:// (%r)' % (parts.scheme,))
        # process options now, directly altering self
        for option, values in urlparse.parse_qs(parts.query, True).items():
            if option == 'dev':
                self.output = open(values[0], 'w')
            elif option == 'color':
                self.color = True
            elif option == 'hex':
                self.hexlify = True
        return ''.join([parts.netloc, parts.path])

    def write(self, tx):
        if self.color:
            self.output.write(self.tx_color)
        if self.hexlify:
            self.output.write(tx.encode('hex'))
        else:
            self.output.write(tx)
        self.output.flush()
        return super(Serial, self).write(tx)

    def read(self, size=1):
        rx = super(Serial, self).read(size)
        if rx:
            if self.color:
                self.output.write(self.rx_color)
            if self.hexlify:
                self.output.write(rx.encode('hex'))
            else:
                self.output.write(rx)
            self.output.flush()
        return rx


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    s = Serial(None)
    s.port = 'spy:///dev/ttyS0'
    print(s)

