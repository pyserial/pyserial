#!/usr/bin/env python

# Very simple serial terminal
# (C)2002-2004 Chris Liechti <cliecht@gmx.net>

# Input characters are sent directly (only LF -> CR/LF/CRLF translation is
# done), received characters are displayed as is (or as trough pythons
# repr, useful for debug purposes)
# Baudrate and echo configuartion is done through globals


import sys, os, serial, threading, getopt

EXITCHARCTER = '\x04'   #ctrl+D

#first choose a platform dependant way to read single characters from the console
if os.name == 'nt':
    import msvcrt
    def getkey():
        while 1:
            if echo:
                z = msvcrt.getche()
            else:
                z = msvcrt.getch()
            if z == '\0' or z == '\xe0':    #functions keys
                msvcrt.getch()
            else:
                if z == '\r':
                    return '\n'
                return z

elif os.name == 'posix':
    import termios, sys, os
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    new = termios.tcgetattr(fd)
    new[3] = new[3] & ~termios.ICANON & ~termios.ECHO
    new[6][termios.VMIN] = 1
    new[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, new)
    s = ''    # We'll save the characters typed and add them to the pool.
    def getkey():
        c = os.read(fd, 1)
        #~ c = sys.stdin.read(1)
        if echo: sys.stdout.write(c); sys.stdout.flush()
        return c
    def clenaup_console():
        termios.tcsetattr(fd, termios.TCSAFLUSH, old)
    sys.exitfunc = clenaup_console      #terminal modes have to be restored on exit...

else:
    raise "Sorry no implementation for your platform (%s) available." % sys.platform

CONVERT_CRLF = 2
CONVERT_CR   = 1
CONVERT_LF   = 0

def reader():
    """loop forever and copy serial->console"""
    while 1:
        data = s.read()
        if repr_mode:
            sys.stdout.write(repr(data)[1:-1])
        else:
            sys.stdout.write(data)
        sys.stdout.flush()

def writer():
    """loop and copy console->serial until EOF character is found"""
    while 1:
        c = getkey()
        if c == EXITCHARCTER: 
            break                       #exit app
        elif c == '\n':
            if convert_outgoing == CONVERT_CRLF:
                s.write('\r\n')         #make it a CR+LF
            elif convert_outgoing == CONVERT_CR:
                s.write('\r')           #make it a CR
            elif convert_outgoing == CONVERT_LF:
                s.write('\n')           #make it a LF
        else:
            s.write(c)                  #send character


#print a short help message
def usage():
    sys.stderr.write("""USAGE: %s [options]
    Miniterm - A simple terminal program for the serial port.

    options:
    -p, --port=PORT: port, a number, default = 0 or a device name
    -b, --baud=BAUD: baudrate, default 9600
    -r, --rtscts:    enable RTS/CTS flow control (default off)
    -x, --xonxoff:   enable software flow control (default off)
    -e, --echo:      enable local echo (default off)
    -c, --cr:        do not send CR+LF, send CR only
    -n, --newline:   do not send CR+LF, send LF only
    -D, --debug:     debug received data (escape nonprintable chars)

""" % (sys.argv[0], ))

if __name__ == '__main__':
    #initialize with defaults
    port  = 0
    baudrate = 9600
    echo = 0
    convert_outgoing = CONVERT_CRLF
    rtscts = 0
    xonxoff = 0
    repr_mode = 0
    
    #parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:],
            "hp:b:rxecnD",
            ["help", "port=", "baud=", "rtscts", "xonxoff", "echo",
            "cr", "newline", "debug"]
        )
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)
    
    for o, a in opts:
        if o in ("-h", "--help"):       #help text
            usage()
            sys.exit()
        elif o in ("-p", "--port"):     #specified port
            try:
                port = int(a)
            except ValueError:
                port = a
        elif o in ("-b", "--baud"):     #specified baudrate
            try:
                baudrate = int(a)
            except ValueError:
                raise ValueError, "Baudrate must be a integer number, not %r" % a
        elif o in ("-r", "--rtscts"):
            rtscts = 1
        elif o in ("-x", "--xonxoff"):
            xonxoff = 1
        elif o in ("-e", "--echo"):
            echo = 1
        elif o in ("-c", "--cr"):
            convert_outgoing = CONVERT_CR
        elif o in ("-n", "--newline"):
            convert_outgoing = CONVERT_LF
        elif o in ("-D", "--debug"):
            repr_mode = 1

    #open the port
    try:
        s = serial.Serial(port, baudrate, rtscts=rtscts, xonxoff=xonxoff)
    except:
        sys.stderr.write("Could not open port\n")
        sys.exit(1)
    sys.stderr.write("--- Miniterm --- type Ctrl-D to quit\n")
    #start serial->console thread
    r = threading.Thread(target=reader)
    r.setDaemon(1)
    r.start()
    #and enter console->serial loop
    writer()

    sys.stderr.write("\n--- exit ---\n")
