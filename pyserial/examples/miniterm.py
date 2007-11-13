#!/usr/bin/env python

# Very simple serial terminal
# (C)2002-2006 Chris Liechti <cliechti@gmx.net>

# Input characters are sent directly (only LF -> CR/LF/CRLF translation is
# done), received characters are displayed as is (or escaped trough pythons
# repr, useful for debug purposes)


import sys, os, serial, threading

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
NEWLINE_CONVERISON_MAP = ('\n', '\r', '\r\n')

class Miniterm:
    def __init__(self, port, baudrate, parity, rtscts, xonxoff, echo=False, convert_outgoing=CONVERT_CRLF, repr_mode=0):
        self.serial = serial.Serial(port, baudrate, parity=parity, rtscts=rtscts, xonxoff=xonxoff, timeout=0.7)
        self.echo = echo
        self.repr_mode = repr_mode
        self.convert_outgoing = convert_outgoing
        self.newline = NEWLINE_CONVERISON_MAP[self.convert_outgoing]

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
        
    def join(self, transmit_only=False):
        self.transmitter_thread.join()
        if not transmit_only:
            self.receiver_thread.join()

    def reader(self):
        """loop and copy serial->console"""
        while self.alive:
            data = self.serial.read(1)
            
            if self.repr_mode == 0:
                # direct output, just have to care about newline setting
                if data == '\r' and self.convert_outgoing == CONVERT_CR:
                    sys.stdout.write('\n')
                else:
                    sys.stdout.write(data)
            elif self.repr_mode == 1:
                # escape non-printable, let pass newlines
                if self.convert_outgoing == CONVERT_CRLF and data in '\r\n':
                    if data == '\n':
                        sys.stdout.write('\n')
                    elif data == '\r':
                        pass
                elif data == '\n' and self.convert_outgoing == CONVERT_LF:
                    sys.stdout.write('\n')
                elif data == '\r' and self.convert_outgoing == CONVERT_CR:
                    sys.stdout.write('\n')
                else:
                    sys.stdout.write(repr(data)[1:-1])
            elif self.repr_mode == 2:
                # escape all non-printable, including newline
                sys.stdout.write(repr(data)[1:-1])
            elif self.repr_mode == 3:
                # escape everything (hexdump)
                for character in data:
                    sys.stdout.write("%s " % character.encode('hex'))
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
                break                                   # exit app
            elif c == '\n':
                self.serial.write(self.newline)         # send newline character(s)
                if self.echo:
                    sys.stdout.write(c)                 #local echo is a real newline in any case
            else:
                self.serial.write(c)                    # send character
                if self.echo:
                    sys.stdout.write(c)



def main():
    import optparse

    parser = optparse.OptionParser(usage="""\
%prog [options] [port [baudrate]]

Miniterm - A simple terminal program for the serial port.""")

    parser.add_option("-p", "--port", dest="port",
        help="port, a number (default 0) or a device name (deprecated option)",
        default=None)
    
    parser.add_option("-b", "--baud", dest="baudrate", action="store", type='int',
        help="set baudrate, default 9600", default=9600)
        
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
        
    parser.add_option("-D", "--debug", dest="repr_mode", action="count",
        help="""debug received data (escape non-printable chars)
--debug can be given multiple times:
0: just print what is received
1: escape non-printable characters, do newlines as ususal
2: escape non-printable characters, newlines too
3: hex dump everything""", default=0)

    parser.add_option("", "--rts", dest="rts_state", action="store", type='int',
        help="set initial RTS line state (possible values: 0, 1)", default=None)

    parser.add_option("", "--dtr", dest="dtr_state", action="store", type='int',
        help="set initial DTR line state (possible values: 0, 1)", default=None)

    parser.add_option("-q", "--quiet", dest="quiet", action="store_true",
        help="suppress non error messages", default=False)


    (options, args) = parser.parse_args()

    if options.cr and options.lf:
        parser.error("ony one of --cr or --lf can be specified")
    
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
    
    convert_outgoing = CONVERT_CRLF
    if options.cr:
        convert_outgoing = CONVERT_CR
    elif options.lf:
        convert_outgoing = CONVERT_LF

    try:
        miniterm = Miniterm(
            port,
            baudrate,
            options.parity,
            rtscts=options.rtscts,
            xonxoff=options.xonxoff,
            echo=options.echo,
            convert_outgoing=convert_outgoing,
            repr_mode=options.repr_mode,
        )
    except serial.SerialException:
        sys.stderr.write("could not open port %r" % port)
        sys.exit(1)

    if not options.quiet:
        sys.stderr.write('--- Miniterm on %s: %d,%s,%s,%s. Type Ctrl-] to quit. ---\n' % (
            miniterm.serial.portstr,
            miniterm.serial.baudrate,
            miniterm.serial.bytesize,
            miniterm.serial.parity,
            miniterm.serial.stopbits,
        ))
    if options.dtr_state is not None:
        if not options.quiet:
            sys.stderr.write('--- forcing DTR %s\n' % (options.dtr_state and 'active' or 'inactive'))
        miniterm.serial.setDTR(options.dtr_state)
    if options.rts_state is not None:
        if not options.quiet:
            sys.stderr.write('--- forcing RTS %s\n' % (options.rts_state and 'active' or 'inactive'))
        miniterm.serial.setRTS(options.rts_state)
        
    miniterm.start()
    miniterm.join(True)
    if not options.quiet:
        sys.stderr.write("\n--- exit ---\n")
    miniterm.join()


if __name__ == '__main__':
    main()
