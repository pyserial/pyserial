#!/usr/bin/env python3
#
# Working with thrading and pySerial
#
# (C) 2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Support threading with serial ports.
"""
import logging
import serial
import threading


class Protocol(object):
    """\
    Protocol as used by the SerialPortWorker. This base class provides empty
    implementations of all methods.
    """

    def connection_made(self, transport):
        """Called when reader thread is started"""

    def data_received(self, data):
        """Called with snippets received from the serial port"""

    def connection_lost(self, exc):
        """\
        Called when the serial port is closed or the reader loop terminated
        otherwise.
        """


class Packetizer(Protocol):
    """read binary packets from serial port"""

    TERMINATOR = b'\0'

    def __init__(self):
        self.buffer = bytearray()
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        self.transport = None

    def data_received(self, data):
        self.buffer.extend(data)
        while self.TERMINATOR in self.buffer:
            packet, self.buffer = self.buffer.split(self.TERMINATOR)
            self.handle_packet(packet)

    def handle_packet(self, packet):
        """Process packets - to be overriden by subclassing"""
        raise NotImplementedError('please implement functionality in handle_packet')


class LineReader(Packetizer):
    """read (unicode) lines from serial port. the encoding is applied"""

    TERMINATOR = b'\n'
    ENCODING = 'utf-8'
    UNICODE_HANDLING = 'replace'

    def handle_packet(self, packet):
        self.handle_line(packet.decode(self.ENCODING, self.UNICODE_HANDLING).rstrip())

    def handle_line(self, line):
        """Process one line - to be overriden by subclassing"""
        raise NotImplementedError('please implement functionality in handle_line')


class SerialPortWorker(threading.Thread):
    """\
    Implement a serial port read loop and dispatch to a Protocol instance (like
    the asyncio.Procotol) but do it with threads.

    Calls to close() will close the serial port but its also possible to just
    stop() this thread and continue the serial port instance otherwise.
    """

    def __init__(self, serial_instance, protocol_factory, use_logging=True):
        """\
        Initialize thread.
        Note that the serial_instance' timeout is set to one second!

        When use_logging, log messages are printed on exceptions.
        """
        super(SerialPortWorker, self).__init__()
        self.daemon = True
        self.serial = serial_instance
        self.protocol_factory = protocol_factory
        self.use_logging = use_logging
        self.alive = True
        self.lock = threading.Lock()
        self._connection_made = threading.Event()
        self.protocol = None

    def stop(self):
        self.alive = False
        self.join(2)

    def run(self):
        """Reader loop"""
        self.protocol = self.protocol_factory()
        self.protocol.connection_made(self)
        self.serial.timeout = 1
        self._connection_made.set()
        while self.alive and self.serial.is_open:
            try:
                # read all that is there or wait for one byte (blocking)
                data = self.serial.read(self.serial.in_waiting or 1)
            except serial.SerialException:
                # probably some IO problem such as disconnected USB serial
                # adapters -> exit
                self.alive = False
                if self.use_logging:
                    logging.exception('Error in %s (thread stops):', self.name)
            else:
                if data:
                    # make a separated try-except for user called code
                    try:
                        self.protocol.data_received(data)
                    except:
                        if self.use_logging:
                            logging.exception('Error in %s (thread continues):', self.name)
        self.protocol.connection_lost(None)
        self.protocol = None

    def write(self, data):
        """Thread safe writing (uses lock)"""
        with self.lock:
            self.serial.write(data)

    def close(self):
        """Close the serial port and exit reader thread (uses lock)"""
        # use the lock to let other threads finish writing
        with self.lock:
            # first stop reading, so that closing can be done on idle port
            self.stop()
            self.serial.close()

    def connect(self):
        """
        Wait until connection is set up and return the transport and protocol
        instances.
        """
        if self.alive:
            self._connection_made.wait()
            return (self, self.protocol)
        else:
            raise RuntimeError('already stopped')

    # - -  context manager, returns protocol

    def __enter__(self):
        self.start()
        self._connection_made.wait()
        return self.protocol

    def __exit__(self, *args, **kwargs):
        self.close()
        

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# test
if __name__ == '__main__':
    import sys
    import time

    class Output(Protocol):
        def connection_made(self, transport):
            self.transport = transport
            sys.stdout.write('port opened: {}\n'.format(transport))
            transport.serial.rts = False
            transport.write(b'hello world\n')

        def data_received(self, data):
            sys.stdout.write('data received: {}\n'.format(repr(data)))

        def connection_lost(self, exc):
            sys.stdout.write('port closed\n')

    ser = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=1)
    t = SerialPortWorker(ser, Output)
    t.start()
    time.sleep(2)
    t.stop()
