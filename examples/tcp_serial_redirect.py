#!/usr/bin/env python
#
# Redirect data from a TCP/IP connection to a serial port and vice versa.
#
# (C) 2002-2009 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

import sys
import os
import time
import threading
import socket
import codecs
import serial

class Redirector(object):
    def __init__(self, serial_instance, socket, spy=False):
        self.serial = serial_instance
        self.socket = socket
        self.spy = spy
        self._write_lock = threading.Lock()

    def shortcut(self):
        """connect the serial port to the TCP port by copying everything
           from one side to the other"""
        self.alive = True
        self.thread_read = threading.Thread(target=self.reader)
        self.thread_read.setDaemon(True)
        self.thread_read.setName('serial->socket')
        self.thread_read.start()
        self.writer()

    def reader(self):
        """loop forever and copy serial->socket"""
        while self.alive:
            try:
                data = self.serial.read(1)              # read one, blocking
                n = self.serial.inWaiting()             # look if there is more
                if n:
                    data = data + self.serial.read(n)   # and get as much as possible
                if data:
                    # the spy shows what's on the serial port, so log it before converting newlines
                    if self.spy:
                        sys.stdout.write(codecs.escape_encode(data)[0])
                        sys.stdout.flush()
                    # escape outgoing data when needed (Telnet IAC (0xff) character)
                    with self._write_lock:
                        self.socket.sendall(data)           # send it over TCP
            except socket.error as msg:
                sys.stderr.write('ERROR: %s\n' % msg)
                # probably got disconnected
                break
        self.alive = False

    def write(self, data):
        """thread safe socket write with no data escaping. used to send telnet stuff"""
        with self._write_lock:
            self.socket.sendall(data)

    def writer(self):
        """loop forever and copy socket->serial"""
        while self.alive:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                self.serial.write(data)                 # get a bunch of bytes and send them
                # the spy shows what's on the serial port, so log it after converting newlines
                if self.spy:
                    sys.stdout.write(codecs.escape_encode(data)[0])
                    sys.stdout.flush()
            except socket.error as msg:
                sys.stderr.write('ERROR: %s\n' % msg)
                # probably got disconnected
                break
        self.alive = False
        self.thread_read.join()

    def stop(self):
        """Stop copying"""
        if self.alive:
            self.alive = False
            self.thread_read.join()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description = "Simple Serial to Network (TCP/IP) redirector.",
        epilog = """\
NOTE: no security measures are implemented. Anyone can remotely connect
to this service over the network.

Only one connection at once is supported. When the connection is terminated
it waits for the next connect.
""")

    parser.add_argument('SERIALPORT',
            help="serial port name")

    parser.add_argument('BAUDRATE',
            type=int,
            nargs='?',
            help='set baud rate, default: %(default)s',
            default=9600)

    parser.add_argument('-q', '--quiet',
            action='store_true',
            help='suppress non error messages',
            default=False)

    parser.add_argument('--spy',
            dest='spy',
            action='store_true',
            help='peek at the communication and print all data to the console',
            default=False)

    group = parser.add_argument_group('serial Port')

    group.add_argument("--parity",
            choices=['N', 'E', 'O', 'S', 'M'],
            type=lambda c: c.upper(),
            help="set parity, one of {N E O S M}, default: N",
            default='N')

    group.add_argument('--rtscts',
            action='store_true',
            help='enable RTS/CTS flow control (default off)',
            default=False)

    group.add_argument('--xonxoff',
            action='store_true',
            help='enable software flow control (default off)',
            default=False)

    group.add_argument('--rts',
            type=int,
            help='set initial RTS line state (possible values: 0, 1)',
            default=None)

    group.add_argument('--dtr',
            type=int,
            help='set initial DTR line state (possible values: 0, 1)',
            default=None)

    group = parser.add_argument_group('network settings')

    group.add_argument('-P', '--localport',
            type=int,
            help='local TCP port',
            default=7777)

    args = parser.parse_args()

    # connect to serial port
    ser = serial.Serial()
    ser.port     = args.SERIALPORT
    ser.baudrate = args.BAUDRATE
    ser.parity   = args.parity
    ser.rtscts   = args.rtscts
    ser.xonxoff  = args.xonxoff
    ser.timeout  = 1     # required so that the reader thread can exit

    if not args.quiet:
        sys.stderr.write("--- TCP/IP to Serial redirector --- type Ctrl-C / BREAK to quit\n")
        sys.stderr.write("--- %s %s,%s,%s,%s ---\n" % (ser.portstr, ser.baudrate, 8, ser.parity, 1))

    try:
        ser.open()
    except serial.SerialException as e:
        sys.stderr.write("Could not open serial port %s: %s\n" % (ser.name, e))
        sys.exit(1)

    if args.rts is not None:
        ser.setRTS(args.rts)

    if args.dtr is not None:
        ser.setDTR(args.dtr)

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind(('', args.localport))
    srv.listen(1)
    while True:
        try:
            sys.stderr.write("Waiting for connection on %s...\n" % args.localport)
            connection, addr = srv.accept()
            sys.stderr.write('Connected by %s\n' % (addr,))
            # enter network <-> serial loop
            r = Redirector(
                ser,
                connection,
                args.spy,
            )
            r.shortcut()
            if args.spy:
                sys.stdout.write('\n')
            sys.stderr.write('Disconnected\n')
            connection.close()
        except KeyboardInterrupt:
            break
        except socket.error as msg:
            sys.stderr.write('ERROR: %s\n' % msg)

    sys.stderr.write('\n--- exit ---\n')

