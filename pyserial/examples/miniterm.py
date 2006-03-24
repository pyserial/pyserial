#!/usr/bin/env python

# Very simple serial terminal
# (C)2002-2006 Chris Liechti <cliechti@gmx.net>

# Input characters are sent directly (only LF -> CR/LF/CRLF translation is
# done), received characters are displayed as is (or as trough pythons
# repr, useful for debug purposes)


import sys, os, serial, threading, getopt

EXITCHARCTER = '\x1d'   #GS/ctrl+]

#first choose a platform dependant way to read single characters from the console
if os.name == 'nt':
    import msvcrt
    def getkey():
        while 1:
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
    def getkey():
        c = os.read(fd, 1)
        return c
    def clenaup_console():
        termios.tcsetattr(fd, termios.TCSAFLUSH, old)
    sys.exitfunc = clenaup_console      #terminal modes have to be restored on exit...

else:
    raise "Sorry no implementation for your platform (%s) available." % sys.platform

CONVERT_CRLF = 2
CONVERT_CR   = 1
CONVERT_LF   = 0

class Miniterm:
    def __init__(self, port, baudrate, parity, rtscts, xonxoff, echo=False, convert_outgoing=CONVERT_CRLF, repr_mode=False):
        self.serial = serial.Serial(port, baudrate, parity=parity, rtscts=rtscts, xonxoff=xonxoff, timeout=1)
        self.echo = echo
        self.repr_mode = repr_mode
        self.convert_outgoing = convert_outgoing

    def start(self):
        self.alive = True
        #start serial->console thread
        self.receiver_thread = threading.Thread(target=self.reader)
        self.receiver_thread.setDaemon(1)
        self.receiver_thread.start()
        #enter console->serial loop
        self.transmitter_thread = threading.Thread(target=self.writer)
        self.transmitter_thread.setDaemon(1)
        self.transmitter_thread.start()
    
    def stop(self):
        self.alive = False
        
    def join(self):
        self.transmitter_thread.join()
        #~ self.receiver_thread.join()

    def reader(self):
        """loop and copy serial->console"""
        while self.alive:
            data = self.serial.read(1)
            if self.repr_mode:
                sys.stdout.write(repr(data)[1:-1])
            else:
                if data == '\r' and self.convert_outgoing == CONVERT_CR:
                    sys.stdout.write('\n')
                else:
                    sys.stdout.write(data)
            sys.stdout.flush()


    def writer(self):
        """loop and copy console->serial until EXITCHARCTER character is found"""
        while self.alive:
            try:
                c = getkey()
            except KeyboardInterrupt:
                c = '\x03'
            if c == EXITCHARCTER: 
                self.stop()
                break                                 #exit app
            elif c == '\n':
                if self.convert_outgoing == CONVERT_CRLF:
                    self.serial.write('\r\n')         #make it a CR+LF
                    if self.echo:
                        sys.stdout.write('\r\n')
                elif self.convert_outgoing == CONVERT_CR:
                    self.serial.write('\r')           #make it a CR
                    if self.echo:
                        sys.stdout.write('\r')
                elif self.convert_outgoing == CONVERT_LF:
                    self.serial.write('\n')           #make it a LF
                    if self.echo:
                        sys.stdout.write('\n')
            else:
                self.serial.write(c)                  #send character
                if self.echo:
                    sys.stdout.write(c)



def main():
    import optparse

    parser = optparse.OptionParser(usage="""\
%prog [options]

Miniterm - A simple terminal program for the serial port.""")

    parser.add_option("-p", "--port", dest="port",
        help="port, a number (default = 0) or a device name", default=0)
    
    parser.add_option("-b", "--baud", dest="baudrate", action="store", type='int',
        help="set baudrate, default=9600", default=9600)
        
    parser.add_option("", "--parity", dest="parity", action="store",
        help="set parity, one of [N, E, O], default=N", default='N')
    
    parser.add_option("-e", "--echo", dest="echo", action="store_true",
        help="enable local echo (default off)", default=False)
        
    parser.add_option("", "--rtscts", dest="rtscts", action="store_true",
        help="enable RTS/CTS flow control (default off)", default=False)
    
    parser.add_option("", "--xonxoff", dest="xonxoff", action="store_true",
        help="enable software flow control (default off)", default=False)
    
    parser.add_option("", "--cr", dest="cr", action="store_true",
        help="do not send CR+LF, send CR only", default=False)
        
    parser.add_option("", "--lf", dest="lf", action="store_true",
        help="do not send CR+LF, send LF only", default=False)
        
    parser.add_option("-D", "--debug", dest="repr_mode", action="store_true",
        help="debug received data (escape nonprintable chars)", default=False)


    (options, args) = parser.parse_args()

    if options.cr and options.lf:
        parser.error("ony one of --cr or --lf can be specified")
    
    if args:
        parser.error("no arguments are allowed, options only")
    
    convert_outgoing = CONVERT_CRLF
    if options.cr:
        convert_outgoing = CONVERT_CR
    elif options.lf:
        convert_outgoing = CONVERT_LF

    try:
        miniterm = Miniterm(
            options.port,
            options.baudrate,
            options.parity,
            rtscts=options.rtscts,
            xonxoff=options.xonxoff,
            echo=options.echo,
            convert_outgoing=convert_outgoing,
            repr_mode=options.repr_mode,
        )
    except serial.SerialException:
        print "could not open port %r" % options.port
        sys.exit(1)

    sys.stderr.write("--- Miniterm on %s--- type Ctrl-] to quit\n" % miniterm.serial.portstr)
    miniterm.start()
    miniterm.join()
    sys.stderr.write("\n--- exit ---\n")

if __name__ == '__main__':
    main()
