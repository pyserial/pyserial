#!/usr/bin/env python

#very simple serial terminal
#input characters are sent directly, received characters are displays as is
#baudrate and echo configuartion is done through globals:


import sys, os, serial, threading, getopt
#EXITCHARCTER = '\x1b'   #ESC
EXITCHARCTER = '\x04'   #ctrl+d

#first choosea platform dependant way to read single characters from the console
if os.name == 'nt': #sys.platform == 'win32':
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
    #XXX: Untested code drrived from the Python FAQ....
    import termios, TERMIOS, sys, os
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    new = termios.tcgetattr(fd)
    new[3] = new[3] & ~TERMIOS.ICANON & ~TERMIOS.ECHO
    new[6][TERMIOS.VMIN] = 1
    new[6][TERMIOS.VTIME] = 0
    termios.tcsetattr(fd, TERMIOS.TCSANOW, new)
    s = ''    # We'll save the characters typed and add them to the pool.
    def getkey():
        c = os.read(fd, 1)
        if echo: sys.stdout.write(c)
        return c
    def clenaup_console():
        termios.tcsetattr(fd, TERMIOS.TCSAFLUSH, old)
    sys.exitfunc = clenaup_console  #terminal modes have to be restored on exit...

else:
    raise "Sorry no implementation for your platform (%s) available." % sys.platform


def reader():
    """loop forever and copy serial->console"""
    while 1:
        sys.stdout.write(s.read())

def writer():
    """loop forever and copy console->serial"""
    while 1:
        c = getkey()
        if c == EXITCHARCTER: break   #exit on esc
        s.write(c)              #send character
        if convert_outgoing_cr and c == '\r':
            s.write('\n')
            if echo: sys.stdout.write('\n')


#print a short help message
def usage():
    print >>sys.stderr, """USAGE: %s [options]
    Simple Terminal Programm for the serial port.

    options:
    -p, --port=PORT: port, a number, defualt = 0 or a device name
    -b, --baud=BAUD: baudrate, default 9600
    -r, --rtscts:    enable RTS/CTS flow control (default off)
    -x, --xonxoff:   enable software flow control (default off)
    -e, --echo:      enable local echo (default off)
    -c, --cr:        disable CR -> CR+LF translation

    """ % sys.argv[0]

if __name__ == '__main__':
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
    echo = 0
    convert_outgoing_cr = 1
    rtscts = 0
    xonxoff = 0
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
