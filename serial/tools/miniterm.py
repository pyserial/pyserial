#!/usr/bin/env python
#
# Very simple serial terminal
#
# (C)2002-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

import codecs
import os
import sys
import threading

import serial
from serial.tools.list_ports import comports

try:
    raw_input
except NameError:
    raw_input = input   # in python3 it's "raw"
    unichr = chr


def key_description(character):
    """generate a readable description for a key"""
    ascii_code = ord(character)
    if ascii_code < 32:
        return 'Ctrl+%c' % (ord('@') + ascii_code)
    else:
        return repr(character)


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

    #  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    # context manager:
    # switch terminal temporary to normal mode (e.g. to get user input)

    def __enter__(self):
        self.cleanup()
        return self

    def __exit__(self, *args, **kwargs):
        self.setup()


if os.name == 'nt':
    import msvcrt
    import ctypes
    class Console(ConsoleBase):
        def __init__(self):
            super(Console, self).__init__()
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
            ctypes.windll.kernel32.SetConsoleCP(65001)
            if sys.version_info < (3, 0):
                class Out:
                    def __init__(self):
                        self.fd = sys.stdout.fileno()
                    def flush(self):
                        pass
                    def write(self, s):
                        os.write(self.fd, s)
                self.output = codecs.getwriter('UTF-8')(Out(), 'replace')
                self.byte_output = Out()
            else:
                self.output = codecs.getwriter('UTF-8')(sys.stdout.buffer, 'replace')

        def getkey(self):
            while True:
                z = msvcrt.getwch()
                if z == '\r':
                    return '\n'
                elif z in '\x00\x0e':    # functions keys, ignore
                    msvcrt.getwch()
                else:
                    return z

elif os.name == 'posix':
    import atexit
    import termios
    class Console(ConsoleBase):
        def __init__(self):
            super(Console, self).__init__()
            self.fd = sys.stdin.fileno()
            self.old = termios.tcgetattr(self.fd)
            atexit.register(self.cleanup)
            if sys.version_info < (3, 0):
                sys.stdin = codecs.getreader(sys.stdin.encoding)(sys.stdin)

        def setup(self):
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
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old)

else:
    raise NotImplementedError("Sorry no implementation for your platform (%s) available." % sys.platform)



class Transform(object):
    """do-nothing: forward all data unchanged"""
    def rx(self, text):
        """text received from serial port"""
        return text

    def tx(self, text):
        """text to be sent to serial port"""
        return text

    def echo(self, text):
        """text to be sent but displayed on console"""
        return text


class CRLF(Transform):
    """ENTER sends CR+LF"""

    def tx(self, text):
        return text.replace('\n', '\r\n')


class CR(Transform):
    """ENTER sends CR"""

    def rx(self, text):
        return text.replace('\r', '\n')

    def tx(self, text):
        return text.replace('\n', '\r')


class LF(Transform):
    """ENTER sends LF"""


class NoTerminal(Transform):
    """remove typical terminal control codes from input"""
    def rx(self, text):
        return ''.join(t if t >= ' ' or t in '\r\n\b\t' else unichr(0x2400 + ord(t)) for t in text)

    echo = rx


class NoControls(Transform):
    """Remove all control codes, incl. CR+LF"""
    def rx(self, text):
        return ''.join(t if t >= ' ' else unichr(0x2400 + ord(t)) for t in text).replace(' ', '\u2423')

    echo = rx


class Printable(Transform):
    """Show decimal code for all non-ASCII characters and replace most control codes"""
    def rx(self, text):
        r = []
        for t in text:
            if ' ' <= t < '\x7f' or t in '\r\n\b\t':
                r.append(t)
            elif t < ' ':
                r.append(unichr(0x2400 + ord(t)))
            else:
                r.extend(unichr(0x2080 + ord(d) - 48) for d in '{:d}'.format(ord(t)))
                r.append(' ')
        return ''.join(r)

    echo = rx


class Colorize(Transform):
    """Apply different colors for received and echo"""
    def __init__(self):
        # XXX make it configurable, use colorama?
        self.input_color = '\x1b[37m'
        self.echo_color = '\x1b[31m'

    def rx(self, text):
        return self.input_color + text

    def echo(self, text):
        return self.echo_color + text


class DebugIO(Transform):
    """Print what is sent and received"""
    def rx(self, text):
        sys.stderr.write(' [RX:{}] '.format(repr(text)))
        sys.stderr.flush()
        return text

    def tx(self, text):
        sys.stderr.write(' [TX:{}] '.format(repr(text)))
        sys.stderr.flush()
        return text


# other ideas:
# - add date/time for each newline
# - insert newline after: a) timeout b) packet end character

TRANSFORMATIONS = {
        'crlf': CRLF,
        'cr': CR,
        'lf': LF,
        'direct': Transform,    # no transformation
        'default': NoTerminal,
        'nocontrol': NoControls,
        'printable': Printable,
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
        self.input_encoding = 'UTF-8'
        self.output_encoding = 'UTF-8'
        self.tx_transformations = [TRANSFORMATIONS[t]() for t in transformations]
        self.rx_transformations = list(reversed(self.tx_transformations))
        self.transformation_names = transformations
        self.exit_character = 0x1d  # GS/CTRL+]
        self.menu_character = 0x14  # Menu: CTRL+T

    def _start_reader(self):
        """Start reader thread"""
        self._reader_alive = True
        # start serial->console thread
        self.receiver_thread = threading.Thread(target=self.reader, name='rx')
        self.receiver_thread.daemon = True
        self.receiver_thread.start()

    def _stop_reader(self):
        """Stop reader thread only, wait for clean exit of thread"""
        self._reader_alive = False
        self.receiver_thread.join()


    def start(self):
        self.alive = True
        self._start_reader()
        # enter console->serial loop
        self.transmitter_thread = threading.Thread(target=self.writer, name='tx')
        self.transmitter_thread.daemon = True
        self.transmitter_thread.start()
        self.console.setup()

    def stop(self):
        self.alive = False

    def join(self, transmit_only=False):
        self.transmitter_thread.join()
        if not transmit_only:
            self.receiver_thread.join()

    def set_rx_encoding(self, encoding, errors='replace'):
        self.input_encoding = encoding
        self.rx_decoder = codecs.getincrementaldecoder(encoding)(errors)

    def set_tx_encoding(self, encoding, errors='replace'):
        self.output_encoding = encoding
        self.tx_encoder = codecs.getincrementalencoder(encoding)(errors)


    def dump_port_settings(self):
        sys.stderr.write("\n--- Settings: {p.name}  {p.baudrate},{p.bytesize},{p.parity},{p.stopbits}\n".format(
                p=self.serial))
        sys.stderr.write('--- RTS: {:8}  DTR: {:8}  BREAK: {:8}\n'.format(
                ('active' if self.rts_state else 'inactive'),
                ('active' if self.dtr_state else 'inactive'),
                ('active' if self.break_state else 'inactive')))
        try:
            sys.stderr.write('--- CTS: {:8}  DSR: {:8}  RI: {:8}  CD: {:8}\n'.format(
                    ('active' if self.serial.getCTS() else 'inactive'),
                    ('active' if self.serial.getDSR() else 'inactive'),
                    ('active' if self.serial.getRI() else 'inactive'),
                    ('active' if self.serial.getCD() else 'inactive')))
        except serial.SerialException:
            # on RFC 2217 ports, it can happen if no modem state notification was
            # yet received. ignore this error.
            pass
        sys.stderr.write('--- software flow control: {}\n'.format('active' if self.serial.xonxoff else 'inactive'))
        sys.stderr.write('--- hardware flow control: {}\n'.format('active' if self.serial.rtscts else 'inactive'))
        #~ sys.stderr.write('--- data escaping: %s  linefeed: %s\n' % (
                #~ REPR_MODES[self.repr_mode],
                #~ LF_MODES[self.convert_outgoing]))
        sys.stderr.write('--- serial input encoding: {}\n'.format(self.input_encoding))
        sys.stderr.write('--- serial output encoding: {}\n'.format(self.output_encoding))
        sys.stderr.write('--- transformations: {}\n'.format(' '.join(self.transformation_names)))

    def reader(self):
        """loop and copy serial->console"""
        try:
            while self.alive and self._reader_alive:
                # read all that is there or wait for one byte
                data = self.serial.read(self.serial.inWaiting() or 1)
                if data:
                    if self.raw:
                        self.console.write_bytes(data)
                    else:
                        text = self.rx_decoder.decode(data)
                        for transformation in self.rx_transformations:
                            text = transformation.rx(text)
                        self.console.write(text)
        except serial.SerialException as e:
            self.alive = False
            # XXX would be nice if the writer could be interrupted at this
            #     point... to exit completely
            raise


    def writer(self):
        """\
        Loop and copy console->serial until self.exit_character character is
        found. When self.menu_character is found, interpret the next key
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
                    self.handle_menu_key(c)
                    menu_active = False
                elif c == self.menu_character:
                    menu_active = True      # next char will be for menu
                elif c == self.exit_character:
                    self.stop()             # exit app
                    break
                else:
                    #~ if self.raw:
                    text = c
                    echo_text = text
                    for transformation in self.tx_transformations:
                        text = transformation.tx(text)
                        echo_text = transformation.echo(echo_text)
                    self.serial.write(self.tx_encoder.encode(text))
                    if self.echo:
                        self.console.write(echo_text)
        except:
            self.alive = False
            raise

    def handle_menu_key(self, c):
        """Implement a simple menu / settings"""
        if c == self.menu_character or c == self.exit_character:
            # Menu/exit character again -> send itself
            self.serial.write(self.tx_encoder.encode(c))
            if self.echo:
                self.console.write(c)
        elif c == '\x15':                       # CTRL+U -> upload file
            sys.stderr.write('\n--- File to upload: ')
            sys.stderr.flush()
            with self.console:
                filename = sys.stdin.readline().rstrip('\r\n')
                if filename:
                    try:
                        with open(filename, 'rb') as f:
                            sys.stderr.write('--- Sending file {} ---\n'.format(filename))
                            while True:
                                block = f.read(1024)
                                if not block:
                                    break
                                self.serial.write(block)
                                # Wait for output buffer to drain.
                                self.serial.flush()
                                sys.stderr.write('.')   # Progress indicator.
                        sys.stderr.write('\n--- File {} sent ---\n'.format(filename))
                    except IOError as e:
                        sys.stderr.write('--- ERROR opening file {}: {} ---\n'.format(filename, e))
        elif c in '\x08hH?':                    # CTRL+H, h, H, ? -> Show help
            sys.stderr.write(self.get_help_text())
        elif c == '\x12':                       # CTRL+R -> Toggle RTS
            self.rts_state = not self.rts_state
            self.serial.setRTS(self.rts_state)
            sys.stderr.write('--- RTS {} ---\n'.format('active' if self.rts_state else 'inactive'))
        elif c == '\x04':                       # CTRL+D -> Toggle DTR
            self.dtr_state = not self.dtr_state
            self.serial.setDTR(self.dtr_state)
            sys.stderr.write('--- DTR {} ---\n'.format('active' if self.dtr_state else 'inactive'))
        elif c == '\x02':                       # CTRL+B -> toggle BREAK condition
            self.break_state = not self.break_state
            self.serial.setBreak(self.break_state)
            sys.stderr.write('--- BREAK {} ---\n'.format('active' if self.break_state else 'inactive'))
        elif c == '\x05':                       # CTRL+E -> toggle local echo
            self.echo = not self.echo
            sys.stderr.write('--- local echo {} ---\n'.format('active' if self.echo else 'inactive'))
        elif c == '\x09':                       # CTRL+I -> info
            self.dump_port_settings()
        #~ elif c == '\x01':                       # CTRL+A -> cycle escape mode
        #~ elif c == '\x0c':                       # CTRL+L -> cycle linefeed mode
        elif c in 'pP':                         # P -> change port
            dump_port_list()
            sys.stderr.write('--- Enter port name: ')
            sys.stderr.flush()
            with self.console:
                try:
                    port = sys.stdin.readline().strip()
                except KeyboardInterrupt:
                    port = None
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
                    sys.stderr.write('--- ERROR opening new port: {} ---\n'.format(e))
                    new_serial.close()
                else:
                    self.serial.close()
                    self.serial = new_serial
                    sys.stderr.write('--- Port changed to: {} ---\n'.format(self.serial.port))
                # and restart the reader thread
                self._start_reader()
        elif c in 'bB':                         # B -> change baudrate
            sys.stderr.write('\n--- Baudrate: ')
            sys.stderr.flush()
            with self.console:
                backup = self.serial.baudrate
                try:
                    self.serial.baudrate = int(sys.stdin.readline().strip())
                except ValueError as e:
                    sys.stderr.write('--- ERROR setting baudrate: %s ---\n'.format(e))
                    self.serial.baudrate = backup
                else:
                    self.dump_port_settings()
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
            sys.stderr.write('--- unknown menu character {} --\n'.format(key_description(c)))

    def get_help_text(self):
        # help text, starts with blank line!
        return """
--- pySerial ({version}) - miniterm - help
---
--- {exit:8} Exit program
--- {menu:8} Menu escape key, followed by:
--- Menu keys:
---    {menu:7} Send the menu character itself to remote
---    {exit:7} Send the exit character itself to remote
---    {info:7} Show info
---    {upload:7} Upload file (prompt will be shown)
--- Toggles:
---    {rts:7} RTS          {echo:7} local echo
---    {dtr:7} DTR          {brk:7} BREAK
---
--- Port settings ({menu} followed by the following):
---    p          change port
---    7 8        set data bits
---    N E O S M  change parity (None, Even, Odd, Space, Mark)
---    1 2 3      set stop bits (1, 2, 1.5)
---    b          change baud rate
---    x X        disable/enable software flow control
---    r R        disable/enable hardware flow control
""".format(
                version=getattr(serial, 'VERSION', 'unknown version'),
                exit=key_description(self.exit_character),
                menu=key_description(self.menu_character),
                rts=key_description('\x12'),
                dtr=key_description('\x04'),
                brk=key_description('\x02'),
                echo=key_description('\x05'),
                info=key_description('\x09'),
                upload=key_description('\x15'),
                )



# default args can be used to override when calling main() from an other script
# e.g to create a miniterm-my-device.py
def main(default_port=None, default_baudrate=9600, default_rts=None, default_dtr=None):
    import argparse

    parser = argparse.ArgumentParser(
            description="Miniterm - A simple terminal program for the serial port.")

    parser.add_argument("port",
            nargs='?',
            help="serial port name",
            default=default_port)

    parser.add_argument("baudrate",
            nargs='?',
            type=int,
            help="set baud rate, default: %(default)s",
            default=default_baudrate)

    group = parser.add_argument_group("port settings")

    group.add_argument("--parity",
            choices=['N', 'E', 'O', 'S', 'M'],
            type=lambda c: c.upper(),
            help="set parity, one of {N E O S M}, default: N",
            default='N')

    group.add_argument("--rtscts",
            action="store_true",
            help="enable RTS/CTS flow control (default off)",
            default=False)

    group.add_argument("--xonxoff",
            action="store_true",
            help="enable software flow control (default off)",
            default=False)

    group.add_argument("--rts",
            type=int,
            help="set initial RTS line state (possible values: 0, 1)",
            default=default_rts)

    group.add_argument("--dtr",
            type=int,
            help="set initial DTR line state (possible values: 0, 1)",
            default=default_dtr)

    group = parser.add_argument_group("data handling")

    group.add_argument("-e", "--echo",
            action="store_true",
            help="enable local echo (default off)",
            default=False)

    group.add_argument("--encoding",
            dest="serial_port_encoding",
            metavar="CODEC",
            help="set the encoding for the serial port, default: %(default)s",
            default='UTF-8')

    group.add_argument("-t", "--transformation",
            dest="transformations",
            action="append",
            metavar="NAME",
            help="add text transformation",
            default=[])

    group.add_argument("--eol",
            choices=['CR', 'LF', 'CRLF'],
            type=lambda c: c.upper(),
            help="end of line mode",
            default='CRLF')

    group.add_argument("--raw",
            action="store_true",
            help="Do no apply any encodings/transformations",
            default=False)

    group = parser.add_argument_group("hotkeys")

    group.add_argument("--exit-char",
            type=int,
            metavar='NUM',
            help="Unicode of special character that is used to exit the application, default: %(default)s",
            default=0x1d  # GS/CTRL+]
            )

    group.add_argument("--menu-char",
            type=int,
            metavar='NUM',
            help="Unicode code of special character that is used to control miniterm (menu), default: %(default)s",
            default=0x14  # Menu: CTRL+T
            )

    group = parser.add_argument_group("diagnostics")

    group.add_argument("-q", "--quiet",
            action="store_true",
            help="suppress non-error messages",
            default=False)

    group.add_argument("--develop",
            action="store_true",
            help="show Python traceback on error",
            default=False)

    args = parser.parse_args()

    if args.menu_char == args.exit_char:
        parser.error('--exit-char can not be the same as --menu-char')


    # no port given on command line -> ask user now
    if args.port is None:
        dump_port_list()
        args.port = raw_input('Enter port name:')

    if args.transformations:
        if 'help' in args.transformations:
            sys.stderr.write('Available Transformations:\n')
            sys.stderr.write('\n'.join(
                    '{:<20} = {.__doc__}'.format(k, v)
                    for k, v in sorted(TRANSFORMATIONS.items())))
            sys.stderr.write('\n')
            sys.exit(1)
        transformations = args.transformations
    else:
        transformations = ['default']

    transformations.insert(0, args.eol.lower())

    try:
        miniterm = Miniterm(
                args.port,
                args.baudrate,
                args.parity,
                rtscts=args.rtscts,
                xonxoff=args.xonxoff,
                echo=args.echo,
                transformations=transformations,
                )
        miniterm.exit_character = unichr(args.exit_char)
        miniterm.menu_character = unichr(args.menu_char)
        miniterm.raw = args.raw
        miniterm.set_rx_encoding(args.serial_port_encoding)
        miniterm.set_tx_encoding(args.serial_port_encoding)
    except serial.SerialException as e:
        sys.stderr.write('could not open port {}: {}\n'.format(repr(args.port), e))
        if args.develop:
            raise
        sys.exit(1)

    if not args.quiet:
        sys.stderr.write('--- Miniterm on {p.name}  {p.baudrate},{p.bytesize},{p.parity},{p.stopbits} ---\n'.format(
                p=miniterm.serial))
        sys.stderr.write('--- Quit: {} | Menu: {} | Help: {} followed by {} ---\n'.format(
                key_description(miniterm.exit_character),
                key_description(miniterm.menu_character),
                key_description(miniterm.menu_character),
                key_description('\x08'),
                ))

    if args.dtr is not None:
        if not args.quiet:
            sys.stderr.write('--- forcing DTR {}\n'.format('active' if args.dtr else 'inactive'))
        miniterm.serial.setDTR(args.dtr)
        miniterm.dtr_state = args.dtr
    if args.rts is not None:
        if not args.quiet:
            sys.stderr.write('--- forcing RTS {}\n'.format('active' if args.rts else 'inactive'))
        miniterm.serial.setRTS(args.rts)
        miniterm.rts_state = args.rts

    miniterm.start()
    try:
        miniterm.join(True)
    except KeyboardInterrupt:
        pass
    if not args.quiet:
        sys.stderr.write("\n--- exit ---\n")
    miniterm.join()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    main()
