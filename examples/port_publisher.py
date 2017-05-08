#! /usr/bin/env python
#
# (C) 2001-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Multi-port serial<->TCP/IP forwarder.
- RFC 2217
- check existence of serial port periodically
- start/stop forwarders
- each forwarder creates a server socket and opens the serial port
- serial ports are opened only once. network connect/disconnect
  does not influence serial port
- only one client per connection
"""
import os
import select
import socket
import sys
import time
import traceback

import serial
import serial.rfc2217
import serial.tools.list_ports

import dbus

# Try to import the avahi service definitions properly. If the avahi module is
# not available, fall back to a hard-coded solution that hopefully still works.
try:
    import avahi
except ImportError:
    class avahi:
        DBUS_NAME = "org.freedesktop.Avahi"
        DBUS_PATH_SERVER = "/"
        DBUS_INTERFACE_SERVER = "org.freedesktop.Avahi.Server"
        DBUS_INTERFACE_ENTRY_GROUP = DBUS_NAME + ".EntryGroup"
        IF_UNSPEC = -1
        PROTO_UNSPEC, PROTO_INET, PROTO_INET6 = -1, 0, 1


class ZeroconfService:
    """\
    A simple class to publish a network service with zeroconf using avahi.
    """

    def __init__(self, name, port, stype="_http._tcp",
                 domain="", host="", text=""):
        self.name = name
        self.stype = stype
        self.domain = domain
        self.host = host
        self.port = port
        self.text = text
        self.group = None

    def publish(self):
        bus = dbus.SystemBus()
        server = dbus.Interface(
            bus.get_object(
                avahi.DBUS_NAME,
                avahi.DBUS_PATH_SERVER
            ),
            avahi.DBUS_INTERFACE_SERVER
        )

        g = dbus.Interface(
            bus.get_object(
                avahi.DBUS_NAME,
                server.EntryGroupNew()
            ),
            avahi.DBUS_INTERFACE_ENTRY_GROUP
        )

        g.AddService(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, dbus.UInt32(0),
                     self.name, self.stype, self.domain, self.host,
                     dbus.UInt16(self.port), self.text)

        g.Commit()
        self.group = g

    def unpublish(self):
        if self.group is not None:
            self.group.Reset()
            self.group = None

    def __str__(self):
        return "{!r} @ {}:{} ({})".format(self.name, self.host, self.port, self.stype)


class Forwarder(ZeroconfService):
    """\
    Single port serial<->TCP/IP forarder that depends on an external select
    loop.
    - Buffers for serial -> network and network -> serial
    - RFC 2217 state
    - Zeroconf publish/unpublish on open/close.
    """

    def __init__(self, device, name, network_port, on_close=None, log=None):
        ZeroconfService.__init__(self, name, network_port, stype='_serial_port._tcp')
        self.alive = False
        self.network_port = network_port
        self.on_close = on_close
        self.log = log
        self.device = device
        self.serial = serial.Serial()
        self.serial.port = device
        self.serial.baudrate = 115200
        self.serial.timeout = 0
        self.socket = None
        self.server_socket = None
        self.rfc2217 = None  # instantiate later, when connecting

    def __del__(self):
        try:
            if self.alive:
                self.close()
        except:
            pass  # XXX errors on shutdown

    def open(self):
        """open serial port, start network server and publish service"""
        self.buffer_net2ser = bytearray()
        self.buffer_ser2net = bytearray()

        # open serial port
        try:
            self.serial.rts = False
            self.serial.open()
        except Exception as msg:
            self.handle_serial_error(msg)

        self.serial_settings_backup = self.serial.get_settings()

        # start the socket server
        # XXX add IPv6 support: use getaddrinfo for socket options, bind to multiple sockets?
        #       info_list = socket.getaddrinfo(None, port, 0, socket.SOCK_STREAM, 0, socket.AI_PASSIVE)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            self.server_socket.getsockopt(
                socket.SOL_SOCKET,
                socket.SO_REUSEADDR
            ) | 1
        )
        self.server_socket.setblocking(0)
        try:
            self.server_socket.bind(('', self.network_port))
            self.server_socket.listen(1)
        except socket.error as msg:
            self.handle_server_error()
            #~ raise
        if self.log is not None:
            self.log.info("{}: Waiting for connection on {}...".format(self.device, self.network_port))

        # zeroconfig
        self.publish()

        # now we are ready
        self.alive = True

    def close(self):
        """Close all resources and unpublish service"""
        if self.log is not None:
            self.log.info("{}: closing...".format(self.device))
        self.alive = False
        self.unpublish()
        if self.server_socket:
            self.server_socket.close()
        if self.socket:
            self.handle_disconnect()
        self.serial.close()
        if self.on_close is not None:
            # ensure it is only called once
            callback = self.on_close
            self.on_close = None
            callback(self)

    def write(self, data):
        """the write method is used by serial.rfc2217.PortManager. it has to
        write to the network."""
        self.buffer_ser2net += data

    def update_select_maps(self, read_map, write_map, error_map):
        """Update dictionaries for select call. insert fd->callback mapping"""
        if self.alive:
            # always handle serial port reads
            read_map[self.serial] = self.handle_serial_read
            error_map[self.serial] = self.handle_serial_error
            # handle serial port writes if buffer is not empty
            if self.buffer_net2ser:
                write_map[self.serial] = self.handle_serial_write
            # handle network
            if self.socket is not None:
                # handle socket if connected
                # only read from network if the internal buffer is not
                # already filled. the TCP flow control will hold back data
                if len(self.buffer_net2ser) < 2048:
                    read_map[self.socket] = self.handle_socket_read
                # only check for write readiness when there is data
                if self.buffer_ser2net:
                    write_map[self.socket] = self.handle_socket_write
                error_map[self.socket] = self.handle_socket_error
            else:
                # no connection, ensure clear buffer
                self.buffer_ser2net = bytearray()
            # check the server socket
            read_map[self.server_socket] = self.handle_connect
            error_map[self.server_socket] = self.handle_server_error

    def handle_serial_read(self):
        """Reading from serial port"""
        try:
            data = os.read(self.serial.fileno(), 1024)
            if data:
                # store data in buffer if there is a client connected
                if self.socket is not None:
                    # escape outgoing data when needed (Telnet IAC (0xff) character)
                    if self.rfc2217:
                        data = serial.to_bytes(self.rfc2217.escape(data))
                    self.buffer_ser2net += data
            else:
                self.handle_serial_error()
        except Exception as msg:
            self.handle_serial_error(msg)

    def handle_serial_write(self):
        """Writing to serial port"""
        try:
            # write a chunk
            n = os.write(self.serial.fileno(), bytes(self.buffer_net2ser))
            # and see how large that chunk was, remove that from buffer
            self.buffer_net2ser = self.buffer_net2ser[n:]
        except Exception as msg:
            self.handle_serial_error(msg)

    def handle_serial_error(self, error=None):
        """Serial port error"""
        # terminate connection
        self.close()

    def handle_socket_read(self):
        """Read from socket"""
        try:
            # read a chunk from the serial port
            data = self.socket.recv(1024)
            if data:
                # Process RFC 2217 stuff when enabled
                if self.rfc2217:
                    data = serial.to_bytes(self.rfc2217.filter(data))
                # add data to buffer
                self.buffer_net2ser += data
            else:
                # empty read indicates disconnection
                self.handle_disconnect()
        except socket.error:
            self.handle_socket_error()

    def handle_socket_write(self):
        """Write to socket"""
        try:
            # write a chunk
            count = self.socket.send(bytes(self.buffer_ser2net))
            # and remove the sent data from the buffer
            self.buffer_ser2net = self.buffer_ser2net[count:]
        except socket.error:
            self.handle_socket_error()

    def handle_socket_error(self):
        """Socket connection fails"""
        self.handle_disconnect()

    def handle_connect(self):
        """Server socket gets a connection"""
        # accept a connection in any case, close connection
        # below if already busy
        connection, addr = self.server_socket.accept()
        if self.socket is None:
            self.socket = connection
            # More quickly detect bad clients who quit without closing the
            # connection: After 1 second of idle, start sending TCP keep-alive
            # packets every 1 second. If 3 consecutive keep-alive packets
            # fail, assume the client is gone and close the connection.
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 1)
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
            self.socket.setblocking(0)
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            if self.log is not None:
                self.log.warning('{}: Connected by {}:{}'.format(self.device, addr[0], addr[1]))
            self.serial.rts = True
            self.serial.dtr = True
            if self.log is not None:
                self.rfc2217 = serial.rfc2217.PortManager(self.serial, self, logger=log.getChild(self.device))
            else:
                self.rfc2217 = serial.rfc2217.PortManager(self.serial, self)
        else:
            # reject connection if there is already one
            connection.close()
            if self.log is not None:
                self.log.warning('{}: Rejecting connect from {}:{}'.format(self.device, addr[0], addr[1]))

    def handle_server_error(self):
        """Socket server fails"""
        self.close()

    def handle_disconnect(self):
        """Socket gets disconnected"""
        # signal disconnected terminal with control lines
        try:
            self.serial.rts = False
            self.serial.dtr = False
        finally:
            # restore original port configuration in case it was changed
            self.serial.apply_settings(self.serial_settings_backup)
            # stop RFC 2217 state machine
            self.rfc2217 = None
            # clear send buffer
            self.buffer_ser2net = bytearray()
            # close network connection
            if self.socket is not None:
                self.socket.close()
                self.socket = None
                if self.log is not None:
                    self.log.warning('{}: Disconnected'.format(self.device))


def test():
    service = ZeroconfService(name="TestService", port=3000)
    service.publish()
    input("Press the ENTER key to unpublish the service ")
    service.unpublish()


if __name__ == '__main__':  # noqa
    import logging
    import argparse

    VERBOSTIY = [
        logging.ERROR,      # 0
        logging.WARNING,    # 1 (default)
        logging.INFO,       # 2
        logging.DEBUG,      # 3
    ]

    parser = argparse.ArgumentParser(
        usage="""\
%(prog)s [options]

Announce the existence of devices using zeroconf and provide
a TCP/IP <-> serial port gateway (implements RFC 2217).

If running as daemon, write to syslog. Otherwise write to stdout.
""",
        epilog="""\
NOTE: no security measures are implemented. Anyone can remotely connect
to this service over the network.

Only one connection at once, per port, is supported. When the connection is
terminated, it waits for the next connect.
""")

    group = parser.add_argument_group("serial port settings")

    group.add_argument(
        "--ports-regex",
        help="specify a regex to search against the serial devices and their descriptions (default: %(default)s)",
        default='/dev/ttyUSB[0-9]+',
        metavar="REGEX")

    group = parser.add_argument_group("network settings")

    group.add_argument(
        "--tcp-port",
        dest="base_port",
        help="specify lowest TCP port number (default: %(default)s)",
        default=7000,
        type=int,
        metavar="PORT")

    group = parser.add_argument_group("daemon")

    group.add_argument(
        "-d", "--daemon",
        dest="daemonize",
        action="store_true",
        help="start as daemon",
        default=False)

    group.add_argument(
        "--pidfile",
        help="specify a name for the PID file",
        default=None,
        metavar="FILE")

    group = parser.add_argument_group("diagnostics")

    group.add_argument(
        "-o", "--logfile",
        help="write messages file instead of stdout",
        default=None,
        metavar="FILE")

    group.add_argument(
        "-q", "--quiet",
        dest="verbosity",
        action="store_const",
        const=0,
        help="suppress most diagnostic messages",
        default=1)

    group.add_argument(
        "-v", "--verbose",
        dest="verbosity",
        action="count",
        help="increase diagnostic messages")

    args = parser.parse_args()

    # set up logging
    logging.basicConfig(level=VERBOSTIY[min(args.verbosity, len(VERBOSTIY) - 1)])
    log = logging.getLogger('port_publisher')

    # redirect output if specified
    if args.logfile is not None:
        class WriteFlushed:
            def __init__(self, fileobj):
                self.fileobj = fileobj

            def write(self, s):
                self.fileobj.write(s)
                self.fileobj.flush()

            def close(self):
                self.fileobj.close()
        sys.stdout = sys.stderr = WriteFlushed(open(args.logfile, 'a'))
        # atexit.register(lambda: sys.stdout.close())

    if args.daemonize:
        # if running as daemon is requested, do the fork magic
        # args.quiet = True
        # do the UNIX double-fork magic, see Stevens' "Advanced
        # Programming in the UNIX Environment" for details (ISBN 0201563177)
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as e:
            log.critical("fork #1 failed: {} ({})\n".format(e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")   # don't prevent unmounting....
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent, save eventual PID before
                if args.pidfile is not None:
                    open(args.pidfile, 'w').write("{}".format(pid))
                sys.exit(0)
        except OSError as e:
            log.critical("fork #2 failed: {} ({})\n".format(e.errno, e.strerror))
            sys.exit(1)

        if args.logfile is None:
            import syslog
            syslog.openlog("serial port publisher")

            # redirect output to syslog
            class WriteToSysLog:
                def __init__(self):
                    self.buffer = ''

                def write(self, s):
                    self.buffer += s
                    if '\n' in self.buffer:
                        output, self.buffer = self.buffer.split('\n', 1)
                        syslog.syslog(output)

                def flush(self):
                    syslog.syslog(self.buffer)
                    self.buffer = ''

                def close(self):
                    self.flush()
            sys.stdout = sys.stderr = WriteToSysLog()

            # ensure the that the daemon runs a normal user, if run as root
        # if os.getuid() == 0:
            #    name, passwd, uid, gid, desc, home, shell = pwd.getpwnam('someuser')
            #    os.setgid(gid)     # set group first
            #    os.setuid(uid)     # set user

    # keep the published stuff in a dictionary
    published = {}
    # get a nice hostname
    hostname = socket.gethostname()

    def unpublish(forwarder):
        """when forwarders die, we need to unregister them"""
        try:
            del published[forwarder.device]
        except KeyError:
            pass
        else:
            log.info("unpublish: {}".format(forwarder))

    alive = True
    next_check = 0
    # main loop
    while alive:
        try:
            # if it is time, check for serial port devices
            now = time.time()
            if now > next_check:
                next_check = now + 5
                connected = [d for d, p, i in serial.tools.list_ports.grep(args.ports_regex)]
                # Handle devices that are published, but no longer connected
                for device in set(published).difference(connected):
                    log.info("unpublish: {}".format(published[device]))
                    unpublish(published[device])
                # Handle devices that are connected but not yet published
                for device in sorted(set(connected).difference(published)):
                    # Find the first available port, starting from specified number
                    port = args.base_port
                    ports_in_use = [f.network_port for f in published.values()]
                    while port in ports_in_use:
                        port += 1
                    published[device] = Forwarder(
                        device,
                        "{} on {}".format(device, hostname),
                        port,
                        on_close=unpublish,
                        log=log)
                    log.warning("publish: {}".format(published[device]))
                    published[device].open()

            # select_start = time.time()
            read_map = {}
            write_map = {}
            error_map = {}
            for publisher in published.values():
                publisher.update_select_maps(read_map, write_map, error_map)
            readers, writers, errors = select.select(
                read_map.keys(),
                write_map.keys(),
                error_map.keys(),
                5)
            # select_end = time.time()
            # print "select used %.3f s" % (select_end - select_start)
            for reader in readers:
                read_map[reader]()
            for writer in writers:
                write_map[writer]()
            for error in errors:
                error_map[error]()
            # print "operation used %.3f s" % (time.time() - select_end)
        except KeyboardInterrupt:
            alive = False
            sys.stdout.write('\n')
        except SystemExit:
            raise
        except:
            #~ raise
            traceback.print_exc()
