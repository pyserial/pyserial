#!/usr/bin/env python
#
# Very simple serial terminal
#
# (C)2002-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

# Input characters are sent directly (only LF -> CR/LF/CRLF translation is
# done), received characters are displayed as is (or escaped through pythons
# repr, useful for debug purposes)

import codecs
import os
import sys
import threading
try:
    from serial.tools.list_ports import comports
except ImportError:
    comports = None

import serial


try:
    raw_input
except NameError:
    raw_input = input   # in python3 it's "raw"
    unichr = chr

EXITCHARCTER = b'\x1d'  # GS/CTRL+]
MENUCHARACTER = b'\x14' # Menu: CTRL+T

DEFAULT_PORT = None
DEFAULT_BAUDRATE = 9600
DEFAULT_RTS = None
DEFAULT_DTR = None


def key_description(character):
    """generate a readable description for a key"""
    ascii_code = ord(character)
    if ascii_code < 32:
        return 'Ctrl+%c' % (ord('@') + ascii_code)
    else:
        return repr(character)


# help text, starts with blank line! it's a function so that the current values
# for the shortcut keys is used and not the value at program start
def get_help_text():
    return """
--- pySerial (%(version)s) - miniterm - help
---
--- %(exit)-8s Exit program
--- %(menu)-8s Menu escape key, followed by:
--- Menu keys:
---    %(itself)-7s Send the menu character itself to remote
---    %(exchar)-7s Send the exit character itself to remote
---    %(info)-7s Show info
---    %(upload)-7s Upload file (prompt will be shown)
--- Toggles:
---    %(rts)-7s RTS          %(echo)-7s local echo
---    %(dtr)-7s DTR          %(break)-7s BREAK
---
--- Port settings (%(menu)s followed by the following):
---    p          change port
---    7 8        set data bits
---    n e o s m  change parity (None, Even, Odd, Space, Mark)
---    1 2 3      set stop bits (1, 2, 1.5)
---    b          change baud rate
---    x X        disable/enable software flow control
---    r R        disable/enable hardware flow control
""" % {
    'version': getattr(serial, 'VERSION', 'unknown version'),
    'exit': key_description(EXITCHARCTER),
    'menu': key_description(MENUCHARACTER),
    'rts': key_description(b'\x12'),
    'dtr': key_description(b'\x04'),
    'break': key_description(b'\x02'),
    'echo': key_description(b'\x05'),
    'info': key_description(b'\x09'),
    'upload': key_description(b'\x15'),
    'itself': key_description(MENUCHARACTER),
    'exchar': key_description(EXITCHARCTER),
}


class ConsoleBase(object):
    def __init__(self):
        if sys.version_info >= (3, 0):
            self.byte_output = sys.stdout.buffer
        else:
            self.byte_output = sys.stdout
        self.output = sys.stdout

    def setup(self):
        pass    # Do nothing for 'nt'

    def cleanup(self):
        pass    # Do nothing for 'nt'

    def getkey(self):
        return None

    def write_bytes(self, s):
        self.byte_output.write(s)
        self.byte_output.flush()

    def write(self, s):
        self.output.write(s)
        self.output.flush()


if os.name == 'nt':
    import msvcrt
    import ctypes
    class Console(ConsoleBase):
        def getkey(self):
            while True:
                z = msvcrt.getwch()
                if z == '\r':
                    return '\n'
                elif z in '\x00\x0e':    # functions keys, ignore
                    msvcrt.getwch()
                else:
                    return z
        
        def write(self, s):
            # works, kind of.. can't print unicode
            self.byte_output.write(s.encode(sys.stdout.encoding, 'replace'))
            #~ sys.stdout.write(s) # fails with encoding errors
            #~ for byte in data:    # fails for python3 as it returns ints instead of b''
            #~ for x in range(len(s)):
                #~ byte = s[x:x+1]
                #~ msvcrt.putwch(byte)     # blocks?!? non-overlapped win io?
        
        def write_bytes(self, data):
            #~ for byte in data:    # fails for python3 as it returns ints instead of b''
            for x in range(len(data)):
                byte = data[x:x+1]
                msvcrt.putch(byte)

elif os.name == 'posix':
    import atexit
    import termios
    class Console(ConsoleBase):
        def __init__(self):
            super(Console, self).__init__()
            self.fd = sys.stdin.fileno()
            self.old = None
            atexit.register(self.cleanup)
            if sys.version_info < (3, 0):
                sys.stdin = codecs.getreader(sys.stdin.encoding)(sys.stdin)

        def setup(self):
            self.old = termios.tcgetattr(self.fd)
            new = termios.tcgetattr(self.fd)
            new[3] = new[3] & ~termios.ICANON & ~termios.ECHO & ~termios.ISIG
            new[6][termios.VMIN] = 1
            new[6][termios.VTIME] = 0
            termios.tcsetattr(self.fd, termios.TCSANOW, new)

        def getkey(self):
            return sys.stdin.read(1)
            #~ c = os.read(self.fd, 1)
            #~ return c

        def cleanup(self):
            if self.old is not None:
                termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old)

else:
    raise NotImplementedError("Sorry no implementation for your platform (%s) available." % sys.platform)


# XXX how to handle multi byte sequences like CRLF?
# codecs.IncrementalEncoder would be a good choice

class Transform(object):
    def input(self, text):
        """text received from serial port"""
        return text

    def output(self, text):
        """text to be sent to serial port"""
        return text

    def echo(self, text):
        """text to be sent but displayed on console"""
        return text

class CRLF(Transform):
    """ENTER sends CR+LF"""
    def input(self, text):
        return text.replace('\r\n', '\n')

    def output(self, text):
        return text.replace('\n', '\r\n')

class CR(Transform):
    """ENTER sends CR"""
    def input(self, text):
        return text.replace('\r', '\n')

    def output(self, text):
        return text.replace('\n', '\r')

class LF(Transform):
    """ENTER sends LF"""


class NoTerminal(Transform):
    """remove typical terminal control codes from input"""
    def input(self, text):
        return ''.join(t if t >= ' ' or t in '\r\n' else unichr(0x2400 + ord(t)) for t in text)

    echo = input


class NoControls(Transform):
    """Remove all control codes, incl. CR+LF"""
    def input(self, text):
        return ''.join(t if t >= ' ' else unichr(0x2400 + ord(t)) for t in text)

    echo = input


class HexDump(Transform):
    """Complete hex dump"""
    def input(self, text):
        return ''.join('{:02x} '.format(ord(t)) for t in text)

    echo = input


class Printable(Transform):
    """Show decimal code for all non-ASCII characters and control codes"""
    def input(self, text):
        r = []
        for t in text:
            if ' ' <= t < '\x7f' or t in '\r\n':
                r.append(t)
            else:
                r.extend(unichr(0x2080 + ord(d) - 48) for d in '{:d}'.format(ord(t)))
                r.append(' ')
        return ''.join(r)

    echo = input



class Colorize(Transform):
    """Apply different colors for input and echo"""
    def __init__(self):
        # XXX make it configurable, use colorama?
        self.input_color = '\x1b[37m'
        self.echo_color = '\x1b[31m'

    def input(self, text):
        return self.input_color + text

    def echo(self, text):
        return self.echo_color + text

class DebugIO(Transform):
    """Apply different colors for input and echo"""
    def input(self, text):
        sys.stderr.write('in: %r\n' % text)
        return text

    def echo(self, text):
        sys.stderr.write('out: %r\n' % text)
        return text

# other ideas:
# - add date/time for each newline
# - insert newline after: a) timeout b) packet end character

TRANSFORMATIONS = {
        'crlf': CRLF,
        'cr': CR,
        'lf': LF,
        'default': NoTerminal,
        'nocontrol': NoControls,
        'printable': Printable,
        'hex': HexDump,
        'colorize': Colorize,
        'debug': DebugIO,
        }


def dump_port_list():
    if comports:
        sys.stderr.write('\n--- Available ports:\n')
        for port, desc, hwid in sorted(comports()):
            #~ sys.stderr.write('--- %-20s %s [%s]\n' % (port, desc, hwid))
            sys.stderr.write('--- %-20s %s\n' % (port, desc))


class Miniterm(object):
    def __init__(self, port, baudrate, parity, rtscts, xonxoff, echo=False, transformations=()):
        self.console = Console()
        self.serial = serial.serial_for_url(port, baudrate, parity=parity, rtscts=rtscts, xonxoff=xonxoff, timeout=1)
        self.echo = echo
        self.dtr_state = True
        self.rts_state = True
        self.break_state = False
        self.raw = False
        self.input_encoding = 'latin1'
        self.input_error_handling = 'replace'
        self.output_encoding = 'latin1'
        self.output_error_handling = 'ignore'
        self.transformations = [TRANSFORMATIONS[t]() for t in transformations]
        self.transformation_names = transformations

    def _start_reader(self):
        """Start reader thread"""
        self._reader_alive = True
        # start serial->console thread
        self.receiver_thread = threading.Thread(target=self.reader)
        self.receiver_thread.setDaemon(True)
        self.receiver_thread.start()

    def _stop_reader(self):
        """Stop reader thread only, wait for clean exit of thread"""
        self._reader_alive = False
        self.receiver_thread.join()


    def start(self):
        self.alive = True
        self._start_reader()
        # enter console->serial loop
        self.transmitter_thread = threading.Thread(target=self.writer)
        self.transmitter_thread.setDaemon(True)
        self.transmitter_thread.start()
        self.console.setup()

    def stop(self):
        self.alive = False

    def join(self, transmit_only=False):
        self.transmitter_thread.join()
        if not transmit_only:
            self.receiver_thread.join()

    def dump_port_settings(self):
        sys.stderr.write("\n--- Settings: %s  %s,%s,%s,%s\n" % (
                self.serial.portstr,
                self.serial.baudrate,
                self.serial.bytesize,
                self.serial.parity,
                self.serial.stopbits))
        sys.stderr.write('--- RTS: %-8s  DTR: %-8s  BREAK: %-8s\n' % (
                (self.rts_state and 'active' or 'inactive'),
                (self.dtr_state and 'active' or 'inactive'),
                (self.break_state and 'active' or 'inactive')))
        try:
            sys.stderr.write('--- CTS: %-8s  DSR: %-8s  RI: %-8s  CD: %-8s\n' % (
                    (self.serial.getCTS() and 'active' or 'inactive'),
                    (self.serial.getDSR() and 'active' or 'inactive'),
                    (self.serial.getRI() and 'active' or 'inactive'),
                    (self.serial.getCD() and 'active' or 'inactive')))
        except serial.SerialException:
            # on RFC 2217 ports, it can happen to no modem state notification was
            # yet received. ignore this error.
            pass
        sys.stderr.write('--- software flow control: %s\n' % (self.serial.xonxoff and 'active' or 'inactive'))
        sys.stderr.write('--- hardware flow control: %s\n' % (self.serial.rtscts and 'active' or 'inactive'))
        #~ sys.stderr.write('--- data escaping: %s  linefeed: %s\n' % (
                #~ REPR_MODES[self.repr_mode],
                #~ LF_MODES[self.convert_outgoing]))
        sys.stderr.write('--- serial input encoding: %s\n' % (self.input_encoding,))
        sys.stderr.write('--- serial output encoding: %s\n' % (self.output_encoding,))
        sys.stderr.write('--- transformations: %s\n' % ' '.join(self.transformation_names))

    def reader(self):
        """loop and copy serial->console"""
        try:
            while self.alive and self._reader_alive:
                data = self.serial.read(1) + self.serial.read(self.serial.inWaiting())
                if data:
                    if self.raw:
                        self.console.write_bytes(data)
                    else:
                        text = codecs.decode(
                                data,
                                self.input_encoding,
                                self.input_error_handling)
                        for transformation in self.transformations:
                            text = transformation.input(text)
                        self.console.write(text)
        except serial.SerialException as e:
            self.alive = False
            # XXX would be nice if the writer could be interrupted at this
            #     point... to exit completely
            raise


    def writer(self):
        """\
        Loop and copy console->serial until EXITCHARCTER character is
        found. When MENUCHARACTER is found, interpret the next key
        locally.
        """
        menu_active = False
        try:
            while self.alive:
                try:
                    c = self.console.getkey()
                except KeyboardInterrupt:
                    c = '\x03'
                if menu_active:
                    if c == MENUCHARACTER or c == EXITCHARCTER: # Menu character again/exit char -> send itself
                        b = codecs.encode(
                                c,
                                self.output_encoding,
                                self.output_error_handling)
                        self.serial.write(b)
                        if self.echo:
                            self.console.write(c)
                    elif c == b'\x15':                       # CTRL+U -> upload file
                        sys.stderr.write('\n--- File to upload: ')
                        sys.stderr.flush()
                        self.console.cleanup()
                        filename = sys.stdin.readline().rstrip('\r\n')
                        if filename:
                            try:
                                with open(filename, 'rb') as f:
                                    sys.stderr.write('--- Sending file %s ---\n' % filename)
                                    while True:
                                        block = f.read(1024)
                                        if not block:
                                            break
                                        self.serial.write(block)
                                        # Wait for output buffer to drain.
                                        self.serial.flush()
                                        sys.stderr.write('.')   # Progress indicator.
                                sys.stderr.write('\n--- File %s sent ---\n' % filename)
                            except IOError as e:
                                sys.stderr.write('--- ERROR opening file %s: %s ---\n' % (filename, e))
                        self.console.setup()
                    elif c in '\x08hH?':                    # CTRL+H, h, H, ? -> Show help
                        sys.stderr.write(get_help_text())
                    elif c == '\x12':                       # CTRL+R -> Toggle RTS
                        self.rts_state = not self.rts_state
                        self.serial.setRTS(self.rts_state)
                        sys.stderr.write('--- RTS %s ---\n' % (self.rts_state and 'active' or 'inactive'))
                    elif c == '\x04':                       # CTRL+D -> Toggle DTR
                        self.dtr_state = not self.dtr_state
                        self.serial.setDTR(self.dtr_state)
                        sys.stderr.write('--- DTR %s ---\n' % (self.dtr_state and 'active' or 'inactive'))
                    elif c == '\x02':                       # CTRL+B -> toggle BREAK condition
                        self.break_state = not self.break_state
                        self.serial.setBreak(self.break_state)
                        sys.stderr.write('--- BREAK %s ---\n' % (self.break_state and 'active' or 'inactive'))
                    elif c == '\x05':                       # CTRL+E -> toggle local echo
                        self.echo = not self.echo
                        sys.stderr.write('--- local echo %s ---\n' % (self.echo and 'active' or 'inactive'))
                    elif c == '\x09':                       # CTRL+I -> info
                        self.dump_port_settings()
                    #~ elif c == '\x01':                       # CTRL+A -> cycle escape mode
                    #~ elif c == '\x0c':                       # CTRL+L -> cycle linefeed mode
                    elif c in 'pP':                         # P -> change port
                        dump_port_list()
                        sys.stderr.write('--- Enter port name: ')
                        sys.stderr.flush()
                        self.console.cleanup()
                        try:
                            port = sys.stdin.readline().strip()
                        except KeyboardInterrupt:
                            port = None
                        self.console.setup()
                        if port and port != self.serial.port:
                            # reader thread needs to be shut down
                            self._stop_reader()
                            # save settings
                            settings = self.serial.getSettingsDict()
                            try:
                                new_serial = serial.serial_for_url(port, do_not_open=True)
                                # restore settings and open
                                new_serial.applySettingsDict(settings)
                                new_serial.open()
                                new_serial.setRTS(self.rts_state)
                                new_serial.setDTR(self.dtr_state)
                                new_serial.setBreak(self.break_state)
                            except Exception as e:
                                sys.stderr.write('--- ERROR opening new port: %s ---\n' % (e,))
                                new_serial.close()
                            else:
                                self.serial.close()
                                self.serial = new_serial
                                sys.stderr.write('--- Port changed to: %s ---\n' % (self.serial.port,))
                            # and restart the reader thread
                            self._start_reader()
                    elif c in 'bB':                         # B -> change baudrate
                        sys.stderr.write('\n--- Baudrate: ')
                        sys.stderr.flush()
                        self.console.cleanup()
                        backup = self.serial.baudrate
                        try:
                            self.serial.baudrate = int(sys.stdin.readline().strip())
                        except ValueError as e:
                            sys.stderr.write('--- ERROR setting baudrate: %s ---\n' % (e,))
                            self.serial.baudrate = backup
                        else:
                            self.dump_port_settings()
                        self.console.setup()
                    elif c == '8':                          # 8 -> change to 8 bits
                        self.serial.bytesize = serial.EIGHTBITS
                        self.dump_port_settings()
                    elif c == '7':                          # 7 -> change to 8 bits
                        self.serial.bytesize = serial.SEVENBITS
                        self.dump_port_settings()
                    elif c in 'eE':                         # E -> change to even parity
                        self.serial.parity = serial.PARITY_EVEN
                        self.dump_port_settings()
                    elif c in 'oO':                         # O -> change to odd parity
                        self.serial.parity = serial.PARITY_ODD
                        self.dump_port_settings()
                    elif c in 'mM':                         # M -> change to mark parity
                        self.serial.parity = serial.PARITY_MARK
                        self.dump_port_settings()
                    elif c in 'sS':                         # S -> change to space parity
                        self.serial.parity = serial.PARITY_SPACE
                        self.dump_port_settings()
                    elif c in 'nN':                         # N -> change to no parity
                        self.serial.parity = serial.PARITY_NONE
                        self.dump_port_settings()
                    elif c == '1':                          # 1 -> change to 1 stop bits
                        self.serial.stopbits = serial.STOPBITS_ONE
                        self.dump_port_settings()
                    elif c == '2':                          # 2 -> change to 2 stop bits
                        self.serial.stopbits = serial.STOPBITS_TWO
                        self.dump_port_settings()
                    elif c == '3':                          # 3 -> change to 1.5 stop bits
                        self.serial.stopbits = serial.STOPBITS_ONE_POINT_FIVE
                        self.dump_port_settings()
                    elif c in 'xX':                         # X -> change software flow control
                        self.serial.xonxoff = (c == 'X')
                        self.dump_port_settings()
                    elif c in 'rR':                         # R -> change hardware flow control
                        self.serial.rtscts = (c == 'R')
                        self.dump_port_settings()
                    else:
                        sys.stderr.write('--- unknown menu character %s --\n' % key_description(c))
                    menu_active = False
                elif c == MENUCHARACTER: # next char will be for menu
                    menu_active = True
                elif c == EXITCHARCTER:
                    self.stop()
                    break                                   # exit app
                else:
                    #~ if self.raw:
                    text = c
                    echo_text = text
                    for transformation in self.transformations:
                        text = transformation.output(text)
                        echo_text = transformation.echo(echo_text)
                    b = codecs.encode(
                            text,
                            self.output_encoding,
                            self.output_error_handling)
                    self.serial.write(b)
                    if self.echo:
                        self.console.write(echo_text)
        except:
            self.alive = False
            raise

def main():
    import optparse

    parser = optparse.OptionParser(
        usage = "%prog [options] [port [baudrate]]",
        description = "Miniterm - A simple terminal program for the serial port."
    )

    group = optparse.OptionGroup(parser, "Port settings")

    group.add_option("-p", "--port",
        dest = "port",
        help = "port, a number or a device name. (deprecated option, use parameter instead)",
        default = DEFAULT_PORT
    )

    group.add_option("-b", "--baud",
        dest = "baudrate",
        action = "store",
        type = 'int',
        help = "set baud rate, default %default",
        default = DEFAULT_BAUDRATE
    )

    group.add_option("--parity",
        dest = "parity",
        action = "store",
        help = "set parity, one of [N, E, O, S, M], default=N",
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
        default = DEFAULT_RTS
    )

    group.add_option("--dtr",
        dest = "dtr_state",
        action = "store",
        type = 'int',
        help = "set initial DTR line state (possible values: 0, 1)",
        default = DEFAULT_DTR
    )

    parser.add_option_group(group)

    group = optparse.OptionGroup(parser, "Data handling")

    group.add_option("-e", "--echo",
        dest = "echo",
        action = "store_true",
        help = "enable local echo (default off)",
        default = False
    )

    group.add_option("-t", "--transformation",
        dest = "transformations",
        action = "append",
        help = "Add text transformation",
        default = []
    )

    group.add_option("--cr",
        dest = "cr",
        action = "store_true",
        help = "do not send CR+LF, send CR only",
        default = False
    )

    group.add_option("--lf",
        dest = "lf",
        action = "store_true",
        help = "do not send CR+LF, send LF only",
        default = False
    )

    group.add_option("--raw",
        dest = "raw",
        action = "store_true",
        help = "Do no apply any encodings/transformations",
        default = False
    )

    parser.add_option_group(group)

    group = optparse.OptionGroup(parser, "Hotkeys")

    group.add_option("--exit-char",
        dest = "exit_char",
        action = "store",
        type = 'int',
        help = "ASCII code of special character that is used to exit the application",
        default = 0x1d
    )

    group.add_option("--menu-char",
        dest = "menu_char",
        action = "store",
        type = 'int',
        help = "ASCII code of special character that is used to control miniterm (menu)",
        default = 0x14
    )

    parser.add_option_group(group)

    group = optparse.OptionGroup(parser, "Diagnostics")

    group.add_option("-q", "--quiet",
        dest = "quiet",
        action = "store_true",
        help = "suppress non-error messages",
        default = False
    )

    group.add_option("", "--develop",
        dest = "develop",
        action = "store_true",
        help = "show Python traceback on error",
        default = False
    )

    parser.add_option_group(group)


    (options, args) = parser.parse_args()

    options.parity = options.parity.upper()
    if options.parity not in 'NEOSM':
        parser.error("invalid parity")

    if options.cr and options.lf:
        parser.error("only one of --cr or --lf can be specified")

    if options.menu_char == options.exit_char:
        parser.error('--exit-char can not be the same as --menu-char')

    global EXITCHARCTER, MENUCHARACTER
    EXITCHARCTER = chr(options.exit_char)
    MENUCHARACTER = chr(options.menu_char)

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
        # no port given on command line -> ask user now
        if port is None:
            dump_port_list()
            port = raw_input('Enter port name:')

    if options.transformations:
        if 'help' in options.transformations:
            sys.stderr.write('Available Transformations:\n')
            sys.stderr.write('\n'.join('{:<20} = {.__doc__}'.format(k,v) for k,v in sorted(TRANSFORMATIONS.items())))
            sys.stderr.write('\n')
            sys.exit(1)
        transformations = options.transformations
    else:
        transformations = ['default']

    if options.cr:
        transformations.append('cr')
    elif options.lf:
        transformations.append('lf')
    else:
        transformations.append('crlf')

    try:
        miniterm = Miniterm(
            port,
            baudrate,
            options.parity,
            rtscts=options.rtscts,
            xonxoff=options.xonxoff,
            echo=options.echo,
            transformations=transformations,
        )
        miniterm.raw = options.raw
    except serial.SerialException as e:
        sys.stderr.write("could not open port %r: %s\n" % (port, e))
        if options.develop:
            raise
        sys.exit(1)

    if not options.quiet:
        sys.stderr.write('--- Miniterm on %s: %d,%s,%s,%s ---\n' % (
            miniterm.serial.portstr,
            miniterm.serial.baudrate,
            miniterm.serial.bytesize,
            miniterm.serial.parity,
            miniterm.serial.stopbits,
        ))
        sys.stderr.write('--- Quit: %s  |  Menu: %s | Help: %s followed by %s ---\n' % (
            key_description(EXITCHARCTER),
            key_description(MENUCHARACTER),
            key_description(MENUCHARACTER),
            key_description(b'\x08'),
        ))

    if options.dtr_state is not None:
        if not options.quiet:
            sys.stderr.write('--- forcing DTR %s\n' % (options.dtr_state and 'active' or 'inactive'))
        miniterm.serial.setDTR(options.dtr_state)
        miniterm.dtr_state = options.dtr_state
    if options.rts_state is not None:
        if not options.quiet:
            sys.stderr.write('--- forcing RTS %s\n' % (options.rts_state and 'active' or 'inactive'))
        miniterm.serial.setRTS(options.rts_state)
        miniterm.rts_state = options.rts_state

    miniterm.start()
    try:
        miniterm.join(True)
    except KeyboardInterrupt:
        pass
    if not options.quiet:
        sys.stderr.write("\n--- exit ---\n")
    miniterm.join()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    main()
