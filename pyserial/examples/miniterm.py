#!/usr/bin/env python

#very simple serial terminal
#input characters are sent directly, received characters are displays as is
#baudrate and echo configuartion is done through globals:
baudrate = 9600
echo = 1
convert_outgoing_cr = 1


import sys, os, serial, threading

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



s = serial.Serial(0,baudrate)

def reader():
    """loop forever and copy serial->console"""
    while 1:
        sys.stdout.write(s.read())

def writer():
    """loop forever and copy console->serial"""
    while 1:
        c = getkey()
        if c == '\x1b': break   #exit on esc
        s.write(c)              #send character
        if convert_outgoing_cr and c == '\r':
            s.write('\n')
            if echo: sys.stdout.write('\n')

print "--- Miniterm --- type ESC to quit"
#start serial->console thread
r = threading.Thread(target=reader)
r.setDaemon(1)
r.start()
#enter console->serial loop
writer()

print "\n--- exit ---"
