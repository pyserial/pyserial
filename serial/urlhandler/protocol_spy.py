#! python
#
# Python Serial Port Extension for Win32, Linux, BSD, Jython
# see __init__.py
#
# This module implements a special URL handler that wraps an other port,
# print the traffic for debugging purposes. With this, it is possible
# to debug the serial port traffic on every application that uses
# serial_for_url.
#
# (C) 2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
# URL format:    spy://port[?option[=value][&option[=value]]]
# options:
# - dev=X   a file or device to write to
# - color   use escape code to colorize output
# - raw     forward raw bytes instead of hexdump
#
# example:
#   redirect output to an other terminal window on Posix (Linux):
#   python -m serial.tools.miniterm spy:///dev/ttyUSB0?dev=/dev/pts/14\&color

import sys
import time

import serial

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


def sixteen(data):
    """\
    yield tuples of hex and ASCII display in multiples of 16. Includes a
    space after 8 bytes and (None, None) after 16 bytes and at the end.
    """
    n = 0
    for b in serial.iterbytes(data):
        yield ('{:02X} '.format(ord(b)), b if b' ' <= b < b'\x7f' else b'.')
        n += 1
        if n == 8:
            yield (' ', ' ')
        elif n > 16:
            yield (None, None)
            n = 0
    while n < 16:
        yield ('   ', ' ')
        n += 1
    yield (None, None)


def hexdump(data):
    """yield lines with hexdump of data"""
    values = []
    ascii = []
    for h, a in sixteen(data):
        if h is None:
            yield ' '.join([
                    ''.join(values),
                    ''.join(ascii)])
            del values[:]
            del ascii[:]
        else:
            values.append(h)
            ascii.append(a)


class FormatRaw(object):
    """forward rx and tx data to output"""

    def __init__(self, output, color):
        self.output = output
        self.color = color
        self.rx_color = '\x1b[32m'
        self.tx_color = '\x1b[31m'

    def rx(self, data):
        if self.color:
            self.output.write(self.rx_color)
        self.output.write(data)
        self.output.flush()

    def tx(self, data):
        if self.color:
            self.output.write(self.tx_color)
        self.output.write(data)
        self.output.flush()

    def control(self, name, value):
        pass


class FormatHexdump(object):
    """\
    Create a hex dump of RX ad TX data, show when control lines are read or
    written.

    output example::

        000000.000 FLSH flushInput
        000002.469 RTS  inactive
        000002.773 RTS  active
        000003.106 TX   C3 B6                                            ..
        000003.107 RX   C3                                               .
        000003.108 RX   B6                                               .
    """

    def __init__(self, output, color):
        self.start_time = time.time()
        self.output = output
        self.color = color
        self.rx_color = '\x1b[32m'
        self.tx_color = '\x1b[31m'
        self.control_color = '\x1b[37m'

    def write_line(self, timestamp, label, value):
        self.output.write('{:010.3f} {:4} {}\n'.format(timestamp, label, value))
        self.output.flush()

    def rx(self, data):
        if self.color:
            self.output.write(self.rx_color)
        for row in hexdump(data):
            self.write_line(time.time() - self.start_time, 'RX', row)

    def tx(self, data):
        if self.color:
            self.output.write(self.tx_color)
        for row in hexdump(data):
            self.write_line(time.time() - self.start_time, 'TX', row)

    def control(self, name, value):
        if self.color:
            self.output.write(self.control_color)
        self.write_line(time.time() - self.start_time, name, value)


class Serial(serial.Serial):
    """Just inherit the native Serial port implementation and patch the port property."""

    def __init__(self, *args, **kwargs):
        super(Serial, self).__init__(*args, **kwargs)
        self.formatter = None

    @serial.Serial.port.setter
    def port(self, value):
        if value is not None:
            serial.Serial.port.__set__(self, self.fromURL(value))

    def fromURL(self, url):
        """extract host and port from an URL string"""
        parts = urlparse.urlsplit(url)
        if parts.scheme != 'spy':
            raise serial.SerialException('expected a string in the form "spy://port[?option[=value][&option[=value]]]": not starting with spy:// (%r)' % (parts.scheme,))
        # process options now, directly altering self
        formatter = FormatHexdump
        color = False
        output = sys.stderr
        for option, values in urlparse.parse_qs(parts.query, True).items():
            if option == 'dev':
                output = open(values[0], 'w')
            elif option == 'color':
                color = True
            elif option == 'raw':
                formatter = FormatRaw
        self.formatter = formatter(output, color)
        return ''.join([parts.netloc, parts.path])

    def write(self, tx):
        self.formatter.tx(tx)
        return super(Serial, self).write(tx)

    def read(self, size=1):
        rx = super(Serial, self).read(size)
        if rx:
            self.formatter.rx(rx)
        return rx


    def flush(self):
        self.formatter.control('FLSH', 'flush')
        super(Serial, self).flush()

    def flushInput(self):
        self.formatter.control('FLSH', 'flushInput')
        super(Serial, self).flush()

    def flushOutput(self):
        self.formatter.control('FLSH', 'flushOutput')
        super(Serial, self).flushOutput()

    def sendBreak(self, duration=0.25):
        self.formatter.control('BRK', 'sendBreak {}'.format(duration))
        super(Serial, self).sendBreak(duration)

    def setBreak(self, level=1):
        self.formatter.control('BRK', 'active' if level else 'inactive')
        super(Serial, self).setBreak(level)

    def setRTS(self, level=1):
        self.formatter.control('RTS', 'active' if level else 'inactive')
        super(Serial, self).setRTS(level)

    def setDTR(self, level=1):
        self.formatter.control('DTR', 'active' if level else 'inactive')
        super(Serial, self).setDTR(level)

    def getCTS(self):
        level = super(Serial, self).getCTS()
        self.formatter.control('CTS', 'active' if level else 'inactive')
        return level

    def getDSR(self):
        level = super(Serial, self).getDSR()
        self.formatter.control('DSR', 'active' if level else 'inactive')
        return level

    def getRI(self):
        level = super(Serial, self).getRI()
        self.formatter.control('RI', 'active' if level else 'inactive')
        return level

    def getCD(self):
        self.formatter.control('CD', 'active' if level else 'inactive')
        level = super(Serial, self).getCD()
        return level

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    s = Serial(None)
    s.port = 'spy:///dev/ttyS0'
    print(s)

