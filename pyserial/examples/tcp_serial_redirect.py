#!/usr/bin/env python

# (C) 2002-2009 Chris Liechti <cliechti@gmx.net>
# redirect data from a TCP/IP connection to a serial port and vice versa
# requires Python 2.2 'cause socket.sendall is used


import sys
import os
import time
import threading
import socket
import codecs
import serial
try:
    True
except NameError:
    True = 1
    False = 0

class Redirector:
    def __init__(self, serial_instance, socket, ser_newline=None, net_newline=None, spy=False):
        self.serial = serial_instance
        self.socket = socket
        self.ser_newline = ser_newline
        self.net_newline = net_newline
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
                    if self.ser_newline and self.net_newline:
                        # do the newline conversion
                        # XXX fails for CR+LF in input when it is cut in half at the begin or end of the string
                        data = net_newline.join(data.split(ser_newline))
                    # escape outgoing data when needed (Telnet IAC (0xff) character)
                    self._write_lock.acquire()
                    try:
                        self.socket.sendall(data)           # send it over TCP
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
                if self.ser_newline and self.net_newline:
                    # do the newline conversion
                    # XXX fails for CR+LF in input when it is cut in half at the begin or end of the string
                    data = ser_newline.join(data.split(net_newline))
                self.serial.write(data)                 # get a bunch of bytes and send them
                # the spy shows what's on the serial port, so log it after converting newlines
                if self.spy:
                    sys.stdout.write(codecs.escape_encode(data)[0])
                    sys.stdout.flush()
            except socket.error, msg:
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
    import optparse

    parser = optparse.OptionParser(
        usage = "%prog [options] [port [baudrate]]",
        description = "Simple Serial to Network (TCP/IP) redirector.",
        epilog = """\
NOTE: no security measures are implemented. Anyone can remotely connect
to this service over the network.

Only one connection at once is supported. When the connection is terminated
it waits for the next connect.
""")

    parser.add_option("-q", "--quiet",
        dest = "quiet",
        action = "store_true",
        help = "suppress non error messages",
        default = False
    )

    parser.add_option("--spy",
        dest = "spy",
        action = "store_true",
        help = "peek at the communication and print all data to the console",
        default = False
    )

    group = optparse.OptionGroup(parser,
        "Serial Port",
        "Serial port settings"
    )
    parser.add_option_group(group)

    group.add_option("-p", "--port",
        dest = "port",
        help = "port, a number (default 0) or a device name",
        default = None
    )

    group.add_option("-b", "--baud",
        dest = "baudrate",
        action = "store",
        type = 'int',
        help = "set baud rate, default: %default",
        default = 9600
    )

    group.add_option("", "--parity",
        dest = "parity",
        action = "store",
        help = "set parity, one of [N, E, O], default=%default",
        default = 'N'
    )

    group.add_option("--rtscts",
        dest = "rtscts",
        action = "store_true",
        help = "enable RTS/CTS flow control (default off)",
        default = False
    )

    group.add_option("--xonxoff",
        dest = "xonxoff",
        action = "store_true",
        help = "enable software flow control (default off)",
        default = False
    )

    group.add_option("--rts",
        dest = "rts_state",
        action = "store",
        type = 'int',
        help = "set initial RTS line state (possible values: 0, 1)",
        default = None
    )

    group.add_option("--dtr",
        dest = "dtr_state",
        action = "store",
        type = 'int',
        help = "set initial DTR line state (possible values: 0, 1)",
        default = None
    )

    group = optparse.OptionGroup(parser,
        "Network settings",
        "Network configuration."
    )
    parser.add_option_group(group)

    group.add_option("-P", "--localport",
        dest = "local_port",
        action = "store",
        type = 'int',
        help = "local TCP port",
        default = 7777
    )

    group = optparse.OptionGroup(parser,
        "Newline Settings",
        "Convert newlines between network and serial port. Conversion is normally disabled and can be enabled by --convert."
    )
    parser.add_option_group(group)

    group.add_option("-c", "--convert",
        dest = "convert",
        action = "store_true",
        help = "enable newline conversion (default off)",
        default = False
    )

    group.add_option("--net-nl",
        dest = "net_newline",
        action = "store",
        help = "type of newlines that are expected on the network (default: %default)",
        default = "LF"
    )

    group.add_option("--ser-nl",
        dest = "ser_newline",
        action = "store",
        help = "type of newlines that are expected on the serial port (default: %default)",
        default = "CR+LF"
    )

    (options, args) = parser.parse_args()

    # get port and baud rate from command line arguments or the option switches
    port = options.port
    baudrate = options.baudrate
    if args:
        if options.port is not None:
            parser.error("no arguments are allowed, options only when --port is given")
        port = args.pop(0)
        if args:
            try:
                baudrate = int(args[0])
            except ValueError:
                parser.error("baud rate must be a number, not %r" % args[0])
            args.pop(0)
        if args:
            parser.error("too many arguments")
    else:
        if port is None: port = 0

    # check newline modes for network connection
    mode = options.net_newline.upper()
    if mode == 'CR':
        net_newline = '\r'
    elif mode == 'LF':
        net_newline = '\n'
    elif mode == 'CR+LF' or mode == 'CRLF':
        net_newline = '\r\n'
    else:
        parser.error("Invalid value for --net-nl. Valid are 'CR', 'LF' and 'CR+LF'/'CRLF'.")

    # check newline modes for serial connection
    mode = options.ser_newline.upper()
    if mode == 'CR':
        ser_newline = '\r'
    elif mode == 'LF':
        ser_newline = '\n'
    elif mode == 'CR+LF' or mode == 'CRLF':
        ser_newline = '\r\n'
    else:
        parser.error("Invalid value for --ser-nl. Valid are 'CR', 'LF' and 'CR+LF'/'CRLF'.")

    # connect to serial port
    ser = serial.Serial()
    ser.port     = port
    ser.baudrate = baudrate
    ser.parity   = options.parity
    ser.rtscts   = options.rtscts
    ser.xonxoff  = options.xonxoff
    ser.timeout  = 1     # required so that the reader thread can exit

    if not options.quiet:
        sys.stderr.write("--- TCP/IP to Serial redirector --- type Ctrl-C / BREAK to quit\n")
        sys.stderr.write("--- %s %s,%s,%s,%s ---\n" % (ser.portstr, ser.baudrate, 8, ser.parity, 1))

    try:
        ser.open()
    except serial.SerialException, e:
        sys.stderr.write("Could not open serial port %s: %s\n" % (ser.portstr, e))
        sys.exit(1)

    if options.rts_state is not None:
        ser.setRTS(options.rts_state)

    if options.dtr_state is not None:
        ser.setDTR(options.dtr_state)

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind( ('', options.local_port) )
    srv.listen(1)
    while True:
        try:
            sys.stderr.write("Waiting for connection on %s...\n" % options.local_port)
            connection, addr = srv.accept()
            sys.stderr.write('Connected by %s\n' % (addr,))
            # enter network <-> serial loop
            r = Redirector(
                ser,
                connection,
                options.convert and ser_newline or None,
                options.convert and net_newline or None,
                options.spy,
            )
            r.shortcut()
            if options.spy: sys.stdout.write('\n')
            sys.stderr.write('Disconnected\n')
            connection.close()
        except KeyboardInterrupt:
            break
        except socket.error, msg:
            sys.stderr.write('ERROR: %s\n' % msg)

    sys.stderr.write('\n--- exit ---\n')

