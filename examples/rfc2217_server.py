#!/usr/bin/env python
#
# redirect data from a TCP/IP connection to a serial port and vice versa
# using RFC 2217
#
# (C) 2009-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

import logging
import os
import socket
import sys
import time
import threading
import serial
import serial.rfc2217

class Redirector(object):
    def __init__(self, serial_instance, socket, debug=False):
        self.serial = serial_instance
        self.socket = socket
        self._write_lock = threading.Lock()
        self.rfc2217 = serial.rfc2217.PortManager(
                self.serial,
                self,
                logger = logging.getLogger('rfc2217.server') if debug else None
                )
        self.log = logging.getLogger('redirector')

    def statusline_poller(self):
        self.log.debug('status line poll thread started')
        while self.alive:
            time.sleep(1)
            self.rfc2217.check_modem_lines()
        self.log.debug('status line poll thread terminated')

    def shortcircuit(self):
        """connect the serial port to the TCP port by copying everything
           from one side to the other"""
        self.alive = True
        self.thread_read = threading.Thread(target=self.reader)
        self.thread_read.setDaemon(True)
        self.thread_read.setName('serial->socket')
        self.thread_read.start()
        self.thread_poll = threading.Thread(target=self.statusline_poller)
        self.thread_poll.setDaemon(True)
        self.thread_poll.setName('status line poll')
        self.thread_poll.start()
        self.writer()

    def reader(self):
        """loop forever and copy serial->socket"""
        self.log.debug('reader thread started')
        while self.alive:
            try:
                data = self.serial.read(1)              # read one, blocking
                n = self.serial.inWaiting()             # look if there is more
                if n:
                    data = data + self.serial.read(n)   # and get as much as possible
                if data:
                    # escape outgoing data when needed (Telnet IAC (0xff) character)
                    data = serial.to_bytes(self.rfc2217.escape(data))
                    with self._write_lock:
                        self.socket.sendall(data)       # send it over TCP
            except socket.error as msg:
                self.log.error('%s' % (msg,))
                # probably got disconnected
                break
        self.alive = False
        self.log.debug('reader thread terminated')

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
                self.serial.write(serial.to_bytes(self.rfc2217.filter(data)))
            except socket.error as msg:
                self.log.error('%s' % (msg,))
                # probably got disconnected
                break
        self.stop()

    def stop(self):
        """Stop copying"""
        self.log.debug('stopping')
        if self.alive:
            self.alive = False
            self.thread_read.join()
            self.thread_poll.join()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description = "RFC 2217 Serial to Network (TCP/IP) redirector.",
        epilog = """\
NOTE: no security measures are implemented. Anyone can remotely connect
to this service over the network.

Only one connection at once is supported. When the connection is terminated
it waits for the next connect.
""")

    parser.add_argument('SERIALPORT')

    parser.add_argument('-p', '--localport',
            type=int,
            help='local TCP port, default: %(default)s',
            metavar='TCPPORT',
            default=2217
            )

    parser.add_argument('-v', '--verbose',
            dest='verbosity',
            action='count',
            help='print more diagnostic messages (option can be given multiple times)',
            default=0
            )

    args = parser.parse_args()

    if args.verbosity > 3:
        args.verbosity = 3
    level = (
            logging.WARNING,
            logging.INFO,
            logging.DEBUG,
            logging.NOTSET,
            )[args.verbosity]
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('root').setLevel(logging.INFO)
    logging.getLogger('rfc2217').setLevel(level)

    # connect to serial port
    ser = serial.serial_for_url(args.SERIALPORT, do_not_open=True)
    ser.timeout  = 3     # required so that the reader thread can exit

    logging.info("RFC 2217 TCP/IP to Serial redirector - type Ctrl-C / BREAK to quit")

    try:
        ser.open()
    except serial.SerialException as e:
        logging.error("Could not open serial port %s: %s" % (ser.name, e))
        sys.exit(1)

    logging.info("Serving serial port: %s" % (ser.name,))
    settings = ser.getSettingsDict()
    # reset control line as no _remote_ "terminal" has been connected yet
    ser.setDTR(False)
    ser.setRTS(False)

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(('', args.localport))
    srv.listen(1)
    logging.info("TCP/IP port: %s" % (args.localport,))
    while True:
        try:
            connection, addr = srv.accept()
            logging.info('Connected by %s:%s' % (addr[0], addr[1]))
            connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            ser.setRTS(True)
            ser.setDTR(True)
            # enter network <-> serial loop
            r = Redirector(
                    ser,
                    connection,
                    args.verbosity > 0
                    )
            try:
                r.shortcircuit()
            finally:
                logging.info('Disconnected')
                r.stop()
                connection.close()
                ser.setDTR(False)
                ser.setRTS(False)
                # Restore port settings (may have been changed by RFC 2217
                # capable client)
                ser.applySettingsDict(settings)
        except KeyboardInterrupt:
            break
        except socket.error as msg:
            logging.error('%s' % (msg,))

    logging.info('--- exit ---')
