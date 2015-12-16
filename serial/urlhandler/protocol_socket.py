#! python
#
# This module implements a simple socket based client.
# It does not support changing any port parameters and will silently ignore any
# requests to do so.
#
# The purpose of this module is that applications using pySerial can connect to
# TCP/IP to serial port converters that do not support RFC 2217.
#
# This file is part of pySerial. https://github.com/pyserial/pyserial
# (C) 2001-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
# URL format:    socket://<host>:<port>[/option[/option...]]
# options:
# - "debug" print diagnostic messages

import logging
import select
import socket
import time
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

from serial.serialutil import SerialBase, SerialException, portNotOpenError, to_bytes

# map log level names to constants. used in from_url()
LOGGER_LEVELS = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        }

POLL_TIMEOUT = 2


class Serial(SerialBase):
    """Serial port implementation for plain sockets."""

    BAUDRATES = (50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800,
                 9600, 19200, 38400, 57600, 115200)

    def open(self):
        """\
        Open port with current settings. This may throw a SerialException
        if the port cannot be opened.
        """
        self.logger = None
        if self._port is None:
            raise SerialException("Port must be configured before it can be used.")
        if self.is_open:
            raise SerialException("Port is already open.")
        try:
            self._socket = socket.create_connection(self.from_url(self.portstr))
        except Exception as msg:
            self._socket = None
            raise SerialException("Could not open port %s: %s" % (self.portstr, msg))

        self._socket.settimeout(POLL_TIMEOUT)  # used for write timeout support :/

        # not that there anything to configure...
        self._reconfigure_port()
        # all things set up get, now a clean start
        self.is_open = True
        if not self._dsrdtr:
            self._update_dtr_state()
        if not self._rtscts:
            self._update_rts_state()
        self.reset_input_buffer()
        self.reset_output_buffer()

    def _reconfigure_port(self):
        """\
        Set communication parameters on opened port. For the socket://
        protocol all settings are ignored!
        """
        if self._socket is None:
            raise SerialException("Can only operate on open ports")
        if self.logger:
            self.logger.info('ignored port configuration change')

    def close(self):
        """Close port"""
        if self.is_open:
            if self._socket:
                try:
                    self._socket.shutdown(socket.SHUT_RDWR)
                    self._socket.close()
                except:
                    # ignore errors.
                    pass
                self._socket = None
            self.is_open = False
            # in case of quick reconnects, give the server some time
            time.sleep(0.3)

    def from_url(self, url):
        """extract host and port from an URL string"""
        parts = urlparse.urlsplit(url)
        if parts.scheme != "socket":
            raise SerialException('expected a string in the form "socket://<host>:<port>[?logging={debug|info|warning|error}]": not starting with socket:// (%r)' % (parts.scheme,))
        try:
            # process options now, directly altering self
            for option, values in urlparse.parse_qs(parts.query, True).items():
                if option == 'logging':
                    logging.basicConfig()   # XXX is that good to call it here?
                    self.logger = logging.getLogger('pySerial.socket')
                    self.logger.setLevel(LOGGER_LEVELS[values[0]])
                    self.logger.debug('enabled logging')
                else:
                    raise ValueError('unknown option: %r' % (option,))
            # get host and port
            host, port = parts.hostname, parts.port
            if not 0 <= port < 65536:
                raise ValueError("port not in range 0...65535")
        except ValueError as e:
            raise SerialException('expected a string in the form "socket://<host>:<port>[?logging={debug|info|warning|error}]": %s' % e)
        return (host, port)

    #  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -

    @property
    def in_waiting(self):
        """Return the number of bytes currently in the input buffer."""
        if not self.is_open:
            raise portNotOpenError
        # Poll the socket to see if it is ready for reading.
        # If ready, at least one byte will be to read.
        lr, lw, lx = select.select([self._socket], [], [], 0)
        return len(lr)

    def read(self, size=1):
        """\
        Read size bytes from the serial port. If a timeout is set it may
        return less characters as requested. With no timeout it will block
        until the requested number of bytes is read.
        """
        if not self.is_open:
            raise portNotOpenError
        data = bytearray()
        if self._timeout is not None:
            timeout = time.time() + self._timeout
        else:
            timeout = None
        while len(data) < size:
            try:
                # an implementation with internal buffer would be better
                # performing...
                block = self._socket.recv(size - len(data))
                if block:
                    data.extend(block)
                else:
                    # no data -> EOF (connection probably closed)
                    break
            except socket.timeout:
                # just need to get out of recv from time to time to check if
                # still alive and timeout did not expire
                pass
            except socket.error as e:
                # connection fails -> terminate loop
                raise SerialException('connection failed (%s)' % e)
            if timeout is not None and time.time() > timeout:
                break
        return bytes(data)

    def write(self, data):
        """\
        Output the given byte string over the serial port. Can block if the
        connection is blocked. May raise SerialException if the connection is
        closed.
        """
        if not self.is_open:
            raise portNotOpenError
        try:
            self._socket.sendall(to_bytes(data))
        except socket.error as e:
            # XXX what exception if socket connection fails
            raise SerialException("socket connection failed: %s" % e)
        return len(data)

    def reset_input_buffer(self):
        """Clear input buffer, discarding all that is in the buffer."""
        if not self.is_open:
            raise portNotOpenError
        if self.logger:
            self.logger.info('ignored reset_input_buffer')

    def reset_output_buffer(self):
        """\
        Clear output buffer, aborting the current output and
        discarding all that is in the buffer.
        """
        if not self.is_open:
            raise portNotOpenError
        if self.logger:
            self.logger.info('ignored reset_output_buffer')

    def send_break(self, duration=0.25):
        """\
        Send break condition. Timed, returns to idle state after given
        duration.
        """
        if not self.is_open:
            raise portNotOpenError
        if self.logger:
            self.logger.info('ignored send_break(%r)' % (duration,))

    def _update_break_state(self):
        """Set break: Controls TXD. When active, to transmitting is
        possible."""
        if self.logger:
            self.logger.info('ignored _update_break_state(%r)' % (self._break_state,))

    def _update_rts_state(self):
        """Set terminal status line: Request To Send"""
        if self.logger:
            self.logger.info('ignored _update_rts_state(%r)' % (self._rts_state,))

    def _update_dtr_state(self):
        """Set terminal status line: Data Terminal Ready"""
        if self.logger:
            self.logger.info('ignored _update_dtr_state(%r)' % (self._dtr_state,))

    @property
    def cts(self):
        """Read terminal status line: Clear To Send"""
        if not self.is_open:
            raise portNotOpenError
        if self.logger:
            self.logger.info('returning dummy for cts')
        return True

    @property
    def dsr(self):
        """Read terminal status line: Data Set Ready"""
        if not self.is_open:
            raise portNotOpenError
        if self.logger:
            self.logger.info('returning dummy for dsr')
        return True

    @property
    def ri(self):
        """Read terminal status line: Ring Indicator"""
        if not self.is_open:
            raise portNotOpenError
        if self.logger:
            self.logger.info('returning dummy for ri')
        return False

    @property
    def cd(self):
        """Read terminal status line: Carrier Detect"""
        if not self.is_open:
            raise portNotOpenError
        if self.logger:
            self.logger.info('returning dummy for cd)')
        return True

    # - - - platform specific - - -

    # works on Linux and probably all the other POSIX systems
    def fileno(self):
        """Get the file handle of the underlying socket for use with select"""
        return self._socket.fileno()


#
# simple client test
if __name__ == '__main__':
    import sys
    s = Serial('socket://localhost:7000')
    sys.stdout.write('%s\n' % s)

    sys.stdout.write("write...\n")
    s.write(b"hello\n")
    s.flush()
    sys.stdout.write("read: %s\n" % s.read(5))

    s.close()
