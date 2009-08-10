#!/usr/bin/env python

# (C) 2009 Chris Liechti <cliechti@gmx.net>
# redirect data from a TCP/IP connection to a serial port and vice versa
# using RFC 2217


import sys
import os
import threading
import time
import socket
import serial
import serial.rfc2217

class Redirector:
    def __init__(self, serial_instance, socket):
        self.serial = serial_instance
        self.socket = socket
        self._write_lock = threading.Lock()
        self.rfc2217 = serial.rfc2217.PortManager(self.serial, self, debug_output=False)

    def statusline_poller(self):
        while self.alive:
            time.sleep(1)
            self.rfc2217.check_modem_lines()

    def shortcut(self):
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
        while self.alive:
            try:
                data = self.serial.read(1)              # read one, blocking
                n = self.serial.inWaiting()             # look if there is more
                if n:
                    data = data + self.serial.read(n)   # and get as much as possible
                if data:
                    # escape outgoing data when needed (Telnet IAC (0xff) character)
                    data = serial.to_bytes(self.rfc2217.escape(data))
                    self._write_lock.acquire()
                    try:
                        self.socket.sendall(data)       # send it over TCP
                    finally:
                        self._write_lock.release()
            except socket.error, msg:
                sys.stderr.write('ERROR: %s\n' % msg)
                # probably got disconnected
                break
        self.alive = False

    def write(self, data):
        """thread safe socket write with no data escaping. used to send telnet stuff"""
        self._write_lock.acquire()
        try:
            self.socket.sendall(data)
        finally:
            self._write_lock.release()

    def writer(self):
        """loop forever and copy socket->serial"""
        while self.alive:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                self.serial.write(serial.to_bytes(self.rfc2217.filter(data)))
            except socket.error, msg:
                sys.stderr.write('ERROR: %s\n' % msg)
                # probably got disconnected
                break
        self.stop()

    def stop(self):
        """Stop copying"""
        if self.alive:
            self.alive = False
            self.thread_read.join()
            self.thread_poll.join()


if __name__ == '__main__':
    import optparse

    parser = optparse.OptionParser(
        usage = "%prog [options] port",
        description = "RFC 2217 Serial to Network (TCP/IP) redirector.",
        epilog = """\
NOTE: no security measures are implemented. Anyone can remotely connect
to this service over the network.

Only one connection at once is supported. When the connection is terminated
it waits for the next connect.
""")

    parser.add_option("-p", "--localport",
        dest = "local_port",
        action = "store",
        type = 'int',
        help = "local TCP port",
        default = 2217
    )

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error('serial port name required as argument')

    # connect to serial port
    ser = serial.Serial()
    ser.port     = args[0]
    ser.timeout  = 3     # required so that the reader thread can exit

    sys.stderr.write("--- RFC 2217 TCP/IP to Serial redirector --- type Ctrl-C / BREAK to quit\n")

    try:
        ser.open()
    except serial.SerialException, e:
        sys.stderr.write("Could not open serial port %s: %s\n" % (ser.portstr, e))
        sys.exit(1)

    sys.stderr.write("--- Serving serial port: %s\n" % (ser.portstr,))
    settings = ser.getSettingsDict()
    # reset contol line as no _remote_ "terminal" has been connected yet
    ser.setDTR(False)
    ser.setRTS(False)

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind( ('', options.local_port) )
    srv.listen(1)
    sys.stderr.write("--- TCP/IP port: %s\n" % (options.local_port,))
    while True:
        try:
            connection, addr = srv.accept()
            sys.stderr.write('Connected by %s:%s \n' % (addr[0], addr[1]))
            connection.setsockopt( socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            ser.setRTS(True)
            ser.setDTR(True)
            # enter network <-> serial loop
            r = Redirector(
                ser,
                connection,
            )
            try:
                r.shortcut()
            finally:
                sys.stderr.write('Disconnected\n')
                r.stop()
                connection.close()
                ser.setDTR(False)
                ser.setRTS(False)
            # Restore port settings (may have been changed by RFC 2217 capable
            # client)
            ser.applySettingsDict(settings)
        except KeyboardInterrupt:
            break
        except socket.error, msg:
            sys.stderr.write('ERROR: %s\n' % msg)

    sys.stderr.write('\n--- exit ---\n')
