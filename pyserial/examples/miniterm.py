#!/usr/bin/env python

#very simple serial terminal
#(C)2002-2004 Chris Liechti <cliecht@gmx.net>

#input characters are sent directly, received characters are displays as is
#baudrate and echo configuartion is done through globals


import sys, os, serial, threading, getopt
#EXITCHARCTER = '\x1b'   #ESC
EXITCHARCTER = '\x04'   #ctrl+d

#first choosea platform dependant way to read single characters from the console
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
                return z

elif os.name == 'posix':
    #XXX: Untested code derived from the Python FAQ....
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


def reader():
    """loop forever and copy serial->console"""
    while 1:
        sys.stdout.write(s.read())
        sys.stdout.flush()

def writer():
    """loop and copy console->serial until EOF character is found"""
    while 1:
        c = getkey()
        if c == EXITCHARCTER: break     #exit on esc
        if convert_outgoing_cr and c == '\n':
            s.write('\r')               #make it a CR+LF (LF below)
        s.write(c)                      #send character


#print a short help message
def usage():
    sys.stderr.write("""USAGE: %s [options]
    Simple Terminal Programm for the serial port.

    options:
    -p, --port=PORT: port, a number, default = 0 or a device name
    -b, --baud=BAUD: baudrate, default 9600
    -r, --rtscts:    enable RTS/CTS flow control (default off)
    -x, --xonxoff:   enable software flow control (default off)
    -e, --echo:      enable local echo (default off)
    -c, --cr:        disable LF -> CR+LF translation

""" % (sys.argv[0], ))

if __name__ == '__main__':
    #parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:],
            "hp:b:rxec",
            ["help", "port=", "baud=", "rtscts", "xonxoff", "echo", "cr"]
        )
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)
    
    port  = 0
    baudrate = 9600
    echo = 0
    convert_outgoing_cr = 1
    rtscts = 0
    xonxoff = 0
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
            convert_outgoing_cr = 0

    try:
        s = serial.Serial(port, baudrate, rtscts=rtscts, xonxoff=xonxoff)
    except:
        print "could not open port"
        sys.exit(1)
    print "--- Miniterm --- type Ctrl-D to quit"
    #start serial->console thread
    r = threading.Thread(target=reader)
    r.setDaemon(1)
    r.start()
    #enter console->serial loop
    writer()

    print "\n--- exit ---"
