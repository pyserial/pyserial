#! python
#
# Python Serial Port Extension for Win32, Linux, BSD
# see __init__.py
#
# This module implements a URL dummy handler for serial_for_url.
#
# (C) 2011 Chris Liechti <cliechti@gmx.net>
# this is distributed under a free software license, see license.txt
#
# URL format:    test://

from serial.serialutil import *
import time
import socket
import logging

# map log level names to constants. used in fromURL()
LOGGER_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    }

class DummySerial(SerialBase):
    """Serial port implementation for plain sockets."""

    def open(self):
        """Open port with current settings. This may throw a SerialException
           if the port cannot be opened."""
        if self._port is None:
            raise SerialException("Port must be configured before it can be used.")
        # not that there anything to configure...
        self._reconfigurePort()
        # all things set up get, now a clean start
        self._is_open = True

    def _reconfigurePort(self):
        """Set communication parameters on opened port. for the test://
        protocol all settings are ignored!"""
        if self.logger:
            self.logger.info('ignored port configuration change')

    def close(self):
        """Close port"""
        if self._is_open:
            self._is_open = False

    def makeDeviceName(self, port):
        raise SerialException("there is no sensible way to turn numbers into URLs")

    def fromURL(self, url):
        """extract host and port from an URL string"""
        if url.lower().startswith("test://"): url = url[7:]
        try:
            # is there a "path" (our options)?
            if '/' in url:
                # cut away options
                url, options = url.split('/', 1)
                # process options now, directly altering self
                for option in options.split('/'):
                    if '=' in option:
                        option, value = option.split('=', 1)
                    else:
                        value = None
                    if option == 'logging':
                        logging.basicConfig()   # XXX is that good to call it here?
                        self.logger = logging.getLogger('pySerial.test')
                        self.logger.setLevel(LOGGER_LEVELS[value])
                        self.logger.debug('enabled logging')
                    else:
                        raise ValueError('unknown option: {!r}'.format(option))
        except ValueError as e:
            raise SerialException('expected a string in the form "[test://][option[/option...]]": {}'.format(e))
        return (host, port)

    #  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -

    def in_waiting(self):
        """Return the number of characters currently in the input buffer."""
        if not self._is_open: raise PortNotOpenError()
        if self.logger:
            # set this one to debug as the function could be called often...
            self.logger.debug('WARNING: in_waiting returns dummy value')
        return 0 # hmmm, see comment in read()

    def read(self, size=1):
        """Read size bytes from the serial port. If a timeout is set it may
        return less characters as requested. With no timeout it will block
        until the requested number of bytes is read."""
        if not self._is_open: raise PortNotOpenError()
        data = '123' # dummy data
        return bytes(data)

    def write(self, data):
        """Output the given string over the serial port. Can block if the
        connection is blocked. May raise SerialException if the connection is
        closed."""
        if not self._is_open: raise PortNotOpenError()
        # nothing done
        return len(data)

    def reset_input_buffer(self):
        """Clear input buffer, discarding all that is in the buffer."""
        if not self._is_open: raise PortNotOpenError()
        if self.logger:
            self.logger.info('ignored reset_input_buffer')

    def reset_output_buffer(self):
        """Clear output buffer, aborting the current output and
        discarding all that is in the buffer."""
        if not self._is_open: raise PortNotOpenError()
        if self.logger:
            self.logger.info('ignored reset_output_buffer')

    def send_break(self, duration=0.25):
        """Send break condition. Timed, returns to idle state after given
        duration."""
        if not self._is_open: raise PortNotOpenError()
        if self.logger:
            self.logger.info('ignored send_break({!r})'.format(duration))

    @property
    def break_condition(self):
        """Set break: Controls TXD. When active, to transmitting is
        possible."""
        return False

    @break_condition.setter
    def break_condition(self, level=True):
        if not self._is_open: raise PortNotOpenError()
        if self.logger:
            self.logger.info(f'ignored break_condition = {level!r}')

    @property
    def rts(self):
        return False

    @rts.setter
    def rts(self, level=True):
        """Set terminal status line: Request To Send"""
        if not self._is_open: raise PortNotOpenError()
        if self.logger:
            self.logger.info(f'ignored rts = {level!r}')

    @property
    def dtr(self):
        return False

    @dtr.setter
    def dtr(self, level=True):
        """Set terminal status line: Data Terminal Ready"""
        if not self._is_open: raise PortNotOpenError()
        if self.logger:
            self.logger.info(f'ignored dtr = {level!r}')

    @property
    def cts(self):
        """Read terminal status line: Clear To Send"""
        if not self._is_open: raise PortNotOpenError()
        if self.logger:
            self.logger.info('returning dummy for cts')
        return True

    @property
    def dsr(self):
        """Read terminal status line: Data Set Ready"""
        if not self._is_open: raise PortNotOpenError()
        if self.logger:
            self.logger.info('returning dummy for dsr')
        return True

    @property
    def ri(self):
        """Read terminal status line: Ring Indicator"""
        if not self._is_open: raise PortNotOpenError()
        if self.logger:
            self.logger.info('returning dummy for ri')
        return False

    @property
    def cd(self):
        """Read terminal status line: Carrier Detect"""
        if not self._is_open: raise PortNotOpenError()
        if self.logger:
            self.logger.info('returning dummy for cd')
        return True

    # - - - platform specific - - -
    # None so far


# assemble Serial class with the platform specific implementation and the base
# for file-like behavior. for Python 2.6 and newer, that provide the new I/O
# library, derive from io.RawIOBase
try:
    import io
except ImportError:
    # classic version with our own file-like emulation
    class Serial(DummySerial, FileLike):
        pass
else:
    # io library present
    class Serial(DummySerial, io.RawIOBase):
        pass


# simple client test
if __name__ == '__main__':
    import sys
    s = Serial('test://logging=debug')
    sys.stdout.write('{}\n'.format(s))

    sys.stdout.write("write...\n")
    s.write("hello\n")
    s.flush()
    sys.stdout.write("read: {}\n".format(s.read(5)))

    s.close()
