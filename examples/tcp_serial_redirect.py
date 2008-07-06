#!/usr/bin/env python

# (C) 2002-2006 Chris Liechti <cliechti@gmx.net>
# redirect data from a TCP/IP connection to a serial port and vice versa
# requires Python 2.2 'cause socket.sendall is used


import sys, os, serial, threading, socket

try:
    True
except NameError:
    True = 1
    False = 0

class Redirector:
    def __init__(self, serial, socket):
        self.serial = serial
        self.socket = socket

    def shortcut(self):
        """connect the serial port to the tcp port by copying everything
           from one side to the other"""
        self.alive = True
        self.thread_read = threading.Thread(target=self.reader)
        self.thread_read.setDaemon(1)
        self.thread_read.start()
        self.writer()
    
    def reader(self):
        """loop forever and copy serial->socket"""
        while self.alive:
            try:
                data = self.serial.read(1)              #read one, blocking
                n = self.serial.inWaiting()             #look if there is more
                if n:
                    data = data + self.serial.read(n)   #and get as much as possible
                if data:
                    self.socket.sendall(data)           #send it over TCP
            except socket.error, msg:
                print msg
                #probably got disconnected
                break
        self.alive = False
    
    def writer(self):
        """loop forever and copy socket->serial"""
        while self.alive:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                self.serial.write(data)                 #get a bunch of bytes and send them
            except socket.error, msg:
                print msg
                #probably got disconnected
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

    parser = optparse.OptionParser(usage="""\
%prog [options] [port [baudrate]]
Simple Serial to Network (TCP/IP) redirector.

Note: no security measures are implemeted. Anyone can remotely connect
to this service over the network.
Only one connection at once is supported. When the connection is terminated
it waits for the next connect.
""")
    parser.add_option("-p", "--port", dest="port",
        help="port, a number (default 0) or a device name (deprecated option)",
        default=None)
    
    parser.add_option("-b", "--baud", dest="baudrate", action="store", type='int',
        help="set baudrate, default 9600", default=9600)
        
    parser.add_option("", "--parity", dest="parity", action="store",
        help="set parity, one of [N, E, O], default=N", default='N')
    
    parser.add_option("", "--rtscts", dest="rtscts", action="store_true",
        help="enable RTS/CTS flow control (default off)", default=False)
    
    parser.add_option("", "--xonxoff", dest="xonxoff", action="store_true",
        help="enable software flow control (default off)", default=False)
    
    parser.add_option("", "--cr", dest="cr", action="store_true",
        help="do not send CR+LF, send CR only", default=False)
        
    parser.add_option("", "--lf", dest="lf", action="store_true",
        help="do not send CR+LF, send LF only", default=False)
    
    parser.add_option("", "--rts", dest="rts_state", action="store", type='int',
        help="set initial RTS line state (possible values: 0, 1)", default=None)

    parser.add_option("", "--dtr", dest="dtr_state", action="store", type='int',
        help="set initial DTR line state (possible values: 0, 1)", default=None)

    parser.add_option("-q", "--quiet", dest="quiet", action="store_true",
        help="suppress non error messages", default=False)

    parser.add_option("-P", "--localport", dest="local_port", action="store", type='int',
        help="local TCP port", default=7777)


    (options, args) = parser.parse_args()

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
                parser.error("baudrate must be a number, not %r" % args[0])
            args.pop(0)
        if args:
            parser.error("too many arguments")
    else:
        if port is None: port = 0

    if options.cr and options.lf:
        parser.error("ony one of --cr or --lf can be specified")

    ser = serial.Serial()
    ser.port    = port
    ser.baudrate = baudrate
    ser.rtscts  = options.rtscts
    ser.xonxoff = options.xonxoff
    ser.timeout = 1     #required so that the reader thread can exit
    
    if not options.quiet:
        print "--- TCP/IP to Serial redirector --- type Ctrl-C / BREAK to quit"
        print "--- %s %s,%s,%s,%s ---" % (ser.portstr, ser.baudrate, 8, ser.parity, 1)

    try:
        ser.open()
    except serial.SerialException, e:
        print "Could not open serial port %s: %s" % (ser.portstr, e)
        sys.exit(1)

    if options.rts_state is not None:
        ser.setRTS(options.rts_state)

    if options.dtr_state is not None:
        ser.setDTR(options.dtr_state)

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind( ('', options.local_port) )
    srv.listen(1)
    while 1:
        try:
            print "Waiting for connection on %s..." % options.local_port
            connection, addr = srv.accept()
            print 'Connected by', addr
            #enter console->serial loop
            r = Redirector(ser, connection)
            r.shortcut()
            print 'Disconnected'
            connection.close()
        except socket.error, msg:
            print msg

    print "\n--- exit ---"
