#!/usr/bin/env python

#(C)2002 Chris Liechti >cliecht@gmx.net>
#redirect data from a TCP/IP connection to a serial port and vice versa
#requires python 2.2 'cause socket.sendall is used

#this program is a hack - do not use it as an example of clean
#threading programming! it's only an example for pyserial.

import sys, os, serial, threading, getopt, socket, time

def reader():
    """loop forever and copy serial->console"""
    global connection
    while 1:
        try:
            if connection:
                connection.sendall(s.read(s.inWaiting()))
            else:
                time.sleep(0.2) #lower CPU usage...
        except socket.error, msg:
            print msg
            if connection: connection.close()
            connection = None
        except:
            pass

def writer():
    """loop forever and copy console->serial"""
    global connection
    try:
        while 1:
            s.write(connection.recv(1024))
    except socket.error, msg:
        print msg


#print a short help message
def usage():
    print >>sys.stderr, """USAGE: %s [options]
    Simple Terminal Programm for the serial port.

    options:
    -p, --port=PORT: serial port, a number, defualt = 0 or a device name
    -b, --baud=BAUD: baudrate, default 9600
    -r, --rtscts:    enable RTS/CTS flow control (default off)
    -x, --xonxoff:   enable software flow control (default off)
    -P, --localport: TCP/IP port on which to run the server (default 7777)
    """ % sys.argv[0]

if __name__ == '__main__':
    connection = None
    
    #parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                "hp:b:rxec",
                ["help", "port=", "baud=", "rtscts", "xonxoff", "echo", "cr"])
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)
    
    port  = 0
    baudrate = 9600
    rtscts = 0
    xonxoff = 0
    localport = 7777
    for o, a in opts:
        if o in ("-h", "--help"):   #help text
            usage()
            sys.exit()
        elif o in ("-p", "--port"):   #specified port
            try:
                port = int(a)
            except ValueError:
                port = a
        elif o in ("-b", "--baud"):   #specified baudrate
            try:
                baudrate = int(a)
            except ValueError:
                raise ValueError, "Baudrate must be a integer number"
        elif o in ("-r", "--rtscts"):
            rtscts = 1
        elif o in ("-x", "--xonxoff"):
            xonxoff = 1
        elif o in ("-P", "--localport"):
            try:
                localport = int(a)
            except ValueError:
                raise ValueError, "local port must be an integer number"

    print "--- TCP/IP to Serial redirector --- type Ctrl-C / BREAK to quit"
    #start serial->tcp/ip thread
    r = threading.Thread(target=reader)
    r.setDaemon(1)
    r.start()

    try:
        s = serial.Serial(port, baudrate, rtscts=rtscts, xonxoff=xonxoff)
    except:
        print "could not open port"
        sys.exit(1)

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind( ('', localport) )
    srv.listen(1)
    while 1:
        try:
            connection, addr = srv.accept()
            print 'Connected by', addr
            #enter console->serial loop
            writer()
        except socket.error, msg:
            print msg
        if connection: connection.close()
        connection = None

    print "\n--- exit ---"
