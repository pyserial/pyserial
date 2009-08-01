#! python
#
# Python Serial Port Extension for Win32, Linux, BSD, Jython
# see __init__.py
#
# This module implements a RFC2217 compatible client. RF2217 descibes a
# protocol to access serial ports over TCP/IP and allows setting the baud rate,
# modem control lines etc.
#
# (C) 2001-2009 Chris Liechti <cliechti@gmx.net>
# this is distributed under a free software license, see license.txt

# TODO:
# - setting control line -> answer is not checked (had problems with one of the
#   severs). consider implementing a compatibility mode flag to make check
#   conditional
# - write timeout not implemented at all
# - telnet negotiation probably not correctly implemented

from serialutil import *
import time
import struct
import socket
import threading
import Queue

def to_bytes(seq):
    b = bytearray()
    for item in seq:
        b.append(item)
    return bytes(b)

# port string is expected to be something like this:
# rfc2217://host:port
# host may be an IP or including domain, whatever.
# port is 0...65535

# telnet protocol characters
IAC  = to_bytes([255]) # Interpret As Command
DONT = to_bytes([254])
DO   = to_bytes([253])
WONT = to_bytes([252])
WILL = to_bytes([251])
IAC_DOUBLED = to_bytes([IAC, IAC])

SE  = to_bytes([240])  # Subnegotiation End
NOP = to_bytes([241])  # No Operation
DM  = to_bytes([242])  # Data Mark
BRK = to_bytes([243])  # Break
IP  = to_bytes([244])  # Interrupt process
AO  = to_bytes([245])  # Abort output
AYT = to_bytes([246])  # Are You There
EC  = to_bytes([247])  # Erase Character
EL  = to_bytes([248])  # Erase Line
GA  = to_bytes([249])  # Go Ahead
SB =  to_bytes([250])  # Subnegotiation Begin

# selected telnet options
BINARY = to_bytes([0]) # 8-bit data path
ECHO = to_bytes([1])   # echo
SGA = to_bytes([3])    # suppress go ahead

# RFC2217
COM_PORT_OPTION = to_bytes([44])

# Client to Access Server
#~ SIGNATURE            text                      text
SET_BAUDRATE = to_bytes([1])
SET_DATASIZE = to_bytes([2])
SET_PARITY = to_bytes([3])
SET_STOPSIZE = to_bytes([4])
SET_CONTROL = to_bytes([5])
NOTIFY_LINESTATE = to_bytes([6])
NOTIFY_MODEMSTATE = to_bytes([7])
FLOWCONTROL_SUSPEND = to_bytes([8])
FLOWCONTROL_RESUME = to_bytes([9])
SET_LINESTATE_MASK = to_bytes([10])
SET_MODEMSTATE_MASK = to_bytes([11])
PURGE_DATA = to_bytes([12])

SERVER_SET_BAUDRATE = to_bytes([101])
SERVER_SET_DATASIZE = to_bytes([102])
SERVER_SET_PARITY = to_bytes([103])
SERVER_SET_STOPSIZE = to_bytes([104])
SERVER_SET_CONTROL = to_bytes([105])
SERVER_NOTIFY_LINESTATE = to_bytes([106])
SERVER_NOTIFY_MODEMSTATE = to_bytes([107])
SERVER_FLOWCONTROL_SUSPEND = to_bytes([108])
SERVER_FLOWCONTROL_RESUME = to_bytes([109])
SERVER_SET_LINESTATE_MASK = to_bytes([110])
SERVER_SET_MODEMSTATE_MASK = to_bytes([111])
SERVER_PURGE_DATA = to_bytes([112])

RFC2217_ANSWER_MAP = {
    SET_BAUDRATE: SERVER_SET_BAUDRATE,
    SET_DATASIZE: SERVER_SET_DATASIZE,
    SET_PARITY: SERVER_SET_PARITY,
    SET_STOPSIZE: SERVER_SET_STOPSIZE,
    SET_CONTROL: SERVER_SET_CONTROL,
    NOTIFY_LINESTATE: SERVER_NOTIFY_LINESTATE,
    NOTIFY_MODEMSTATE: SERVER_NOTIFY_MODEMSTATE,
    FLOWCONTROL_SUSPEND: SERVER_FLOWCONTROL_SUSPEND,
    FLOWCONTROL_RESUME: SERVER_FLOWCONTROL_RESUME,
    SET_LINESTATE_MASK: SERVER_SET_LINESTATE_MASK,
    SET_MODEMSTATE_MASK: SERVER_SET_MODEMSTATE_MASK,
    PURGE_DATA: SERVER_PURGE_DATA,
}

SET_CONTROL_REQ_FLOW_SETTING = to_bytes([0])        # Request Com Port Flow Control Setting (outbound/both)
SET_CONTROL_USE_NO_FLOW_CONTROL = to_bytes([1])     # Use No Flow Control (outbound/both)
SET_CONTROL_USE_SW_FLOW_CONTROL = to_bytes([2])     # Use XON/XOFF Flow Control (outbound/both)
SET_CONTROL_USE_HW_FLOW_CONTROL = to_bytes([3])     # Use HARDWARE Flow Control (outbound/both)
SET_CONTROL_REQ_BREAK_STATE = to_bytes([4])         # Request BREAK State
SET_CONTROL_BREAK_ON = to_bytes([5])                # Set BREAK State ON
SET_CONTROL_BREAK_OFF = to_bytes([6])               # Set BREAK State OFF
SET_CONTROL_REQ_DTR = to_bytes([7])                 # Request DTR Signal State
SET_CONTROL_DTR_ON = to_bytes([8])                  # Set DTR Signal State ON
SET_CONTROL_DTR_OFF = to_bytes([9])                 # Set DTR Signal State OFF
SET_CONTROL_REQ_RTS = to_bytes([10])                # Request RTS Signal State
SET_CONTROL_RTS_ON = to_bytes([11])                 # Set RTS Signal State ON
SET_CONTROL_RTS_OFF = to_bytes([12])                # Set RTS Signal State OFF
SET_CONTROL_REQ_FLOW_SETTING_IN = to_bytes([13])    # Request Com Port Flow Control Setting (inbound)
SET_CONTROL_USE_NO_FLOW_CONTROL_IN = to_bytes([14]) # Use No Flow Control (inbound)
SET_CONTROL_USE_SW_FLOW_CONTOL_IN = to_bytes([15])  # Use XON/XOFF Flow Control (inbound)
SET_CONTROL_USE_HW_FLOW_CONTOL_IN = to_bytes([16])  # Use HARDWARE Flow Control (inbound)
SET_CONTROL_USE_DCD_FLOW_CONTROL = to_bytes([17])   # Use DCD Flow Control (outbound/both)
SET_CONTROL_USE_DTR_FLOW_CONTROL = to_bytes([18])   # Use DTR Flow Control (inbound)
SET_CONTROL_USE_DSR_FLOW_CONTROL = to_bytes([19])   # Use DSR Flow Control (outbound/both)

LINESTATE_MASK_TIMEOUT = 128            # Time-out Error
LINESTATE_MASK_SHIFTREG_EMPTY = 64      # Transfer Shift Register Empty
LINESTATE_MASK_TRANSREG_EMPTY = 32      # Transfer Holding Register Empty
LINESTATE_MASK_BREAK_DETECT = 16        # Break-detect Error
LINESTATE_MASK_FRAMING_ERROR = 8        # Framing Error
LINESTATE_MASK_PARTIY_ERROR = 4         # Parity Error
LINESTATE_MASK_OVERRUN_ERROR = 2        # Overrun Error
LINESTATE_MASK_DATA_READY = 1           # Data Ready

MODEMSTATE_MASK_CD = 128        # Receive Line Signal Detect (also known as Carrier Detect)
MODEMSTATE_MASK_RI = 64         # Ring Indicator
MODEMSTATE_MASK_DSR = 32        # Data-Set-Ready Signal State
MODEMSTATE_MASK_CTS = 16        # Clear-To-Send Signal State
MODEMSTATE_MASK_CD_CHANGE = 8   # Delta Receive Line Signal Detect
MODEMSTATE_MASK_RI_CHANGE = 4   # Trailing-edge Ring Detector
MODEMSTATE_MASK_DSR_CHANGE = 2  # Delta Data-Set-Ready
MODEMSTATE_MASK_CTS_CHANGE = 1  # Delta Clear-To-Send

PURGE_RECEIVE_BUFFER = to_bytes([1])        # Purge access server receive data buffer
PURGE_TRANSMIT_BUFFER = to_bytes([2])       # Purge access server transmit data buffer
PURGE_BOTH_BUFFERS = to_bytes([3])          # Purge both the access server receive data buffer and the access server transmit data buffer


RFC2217_PARITY_MAP = {
    PARITY_NONE: 1,
    PARITY_ODD: 2,
    PARITY_EVEN: 3,
    PARITY_MARK: 4,
    PARITY_SPACE: 5,
}

RFC2217_STOPBIT_MAP = {
    STOPBITS_ONE: 1,
    STOPBITS_ONE_POINT_FIVE: 3,
    STOPBITS_TWO: 2,
}

TELNET_ACTION_SUCCESS_MAP = {
    DO:   (DO, WILL),
    WILL: (DO, WILL),
    DONT: (DONT, WONT),
    WONT: (DONT, WONT),
}

class RFC2217Serial(SerialBase):
    """Serial port implemenation for RFC2217 remote serial ports"""

    BAUDRATES = (50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800,
                 9600, 19200, 38400, 57600, 115200)

    def open(self):
        """Open port with current settings. This may throw a SerialException
           if the port cannot be opened."""
        if self._port is None:
            raise SerialException("Port must be configured before it can be used.")
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect(self.fromURL(self.portstr))
        except Exception, msg:
            self._socket = None
            raise SerialException("Could not open port %s: %s" % (self.portstr, msg))

        self._socket.settimeout(5)

        self._read_buffer = Queue.Queue()
        self._telnet_negotiated_options = {}
        self._rfc2217_negotiated_options = {}
        self._linestate = 0
        self._modemstate = 0

        self._thread = threading.Thread(target=self._read_loop)
        self._thread.setDaemon(True)
        self._thread.setName('pySerial RFC2217 reader thread for %s' % (self._port,))
        self._thread.start()

        # negotiate Telnet/RFC2217
        self._negotiate_telnet_option(DO, BINARY)
        #~ self._negotiate_telnet_option(DONT, ECHO)
        if self._negotiate_telnet_option(DO, COM_PORT_OPTION) in (WILL, DO):
            raise SerialException("Remote does not seem to support RFC2217")

        # fine, go on, set RFC2271 specific things
        self._reconfigurePort()
        self._isOpen = True
        if not self._rtscts:
            self.setRTS(True)
            self.setDTR(True)
        self.flushInput()
        self.flushOutput()

    def _reconfigurePort(self):
        """Set communication parameters on opened port."""
        if self._socket is None:
            raise SerialException("Can only operate on open ports")

        #~ if self._timeout is None:
        # XXX set socket timeout to this value?

        # if self._timeout != 0 and self._interCharTimeout is not None:
            # timeouts = (int(self._interCharTimeout * 1000),) + timeouts[1:]
            # XXX

        if self._writeTimeout is not None:
            raise NotImplementedError('writeTimeout is currently not supported')
        # XXX again...


        # Setup the connection info.
        self._set_comport_option(SET_BAUDRATE, struct.pack('!I', self._baudrate))
        self._set_comport_option(SET_DATASIZE, struct.pack('!B', self._bytesize))
        self._set_comport_option(SET_PARITY,   struct.pack('!B', RFC2217_PARITY_MAP[self._parity]))
        self._set_comport_option(SET_STOPSIZE, struct.pack('!B', RFC2217_STOPBIT_MAP[self._stopbits]))

        if self._rtscts and self._xonxoff:
            # XXX this is probably not supported by the server...
            self._set_comport_option(SET_CONTROL, SET_CONTROL_USE_HW_FLOW_CONTROL)
            self._set_comport_option(SET_CONTROL, SET_CONTROL_USE_SW_FLOW_CONTROL)
        elif self._rtscts:
            self._set_comport_option(SET_CONTROL, SET_CONTROL_USE_HW_FLOW_CONTROL)
        elif self._xonxoff:
            self._set_comport_option(SET_CONTROL, SET_CONTROL_USE_SW_FLOW_CONTROL)
        else:
            self._set_comport_option(SET_CONTROL, SET_CONTROL_USE_NO_FLOW_CONTROL)

    def close(self):
        """Close port"""
        if self._isOpen:
            if self._socket:
                try:
                    self._socket.shutdown(socket.SHUT_RDWR)
                    self._socket.close()
                except:
                    # ignore errors.
                    pass
                self._socket = None
            if self._thread:
                self._thread.join()
            self._isOpen = False
            # in case of quick reconnects, give the server some time
            time.sleep(0.3)

    def makeDeviceName(self, port):
        raise SerialException("there is no sensible way to turn numbers into URLs")

    def fromURL(self, url):
        if url.lower().startswith("rfc2217://"): url = url[10:]
        try:
            host, port = url.split(':', 1) # may raise ValueError because of unpacking
            port = int(port)               # and this if it's not a number
            if not 0 <= port < 65536: raise ValueError("port not in range 0...65535")
        except ValueError, e:
            raise SerialException('expected a string in the form "[rfc2217://]host:port": %s' % e)
        return (host, port)

    #  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -

    def inWaiting(self):
        """Return the number of characters currently in the input buffer."""
        if not self._isOpen: raise portNotOpenError
        return self._read_buffer.qsize()

    def read(self, size=1):
        """Read size bytes from the serial port. If a timeout is set it may
        return less characters as requested. With no timeout it will block
        until the requested number of bytes is read."""
        if not self._isOpen: raise portNotOpenError
        data = bytearray()
        try:
            while len(data) < size:
                data.append(self._read_buffer.get(True, self._timeout))
        except Queue.Empty: # -> timeout
            pass
        return bytes(data)

    def write(self, data):
        """Output the given string over the serial port. Can block if the
        connection is blocked. May raise SerialException if the connection is
        closed."""
        if not self._isOpen: raise portNotOpenError
        try:
            self._socket.sendall(data.replace(IAC, IAC_DOUBLED))
        except socket.error, e:
            raise SerialException("socket connection failed: %s" % e) # XXX what exception if socket connection fails
        return len(data)

    def flushInput(self):
        """Clear input buffer, discarding all that is in the buffer."""
        if not self._isOpen: raise portNotOpenError
        self._set_comport_option(PURGE_DATA, PURGE_RECEIVE_BUFFER)
        # empty read buffer
        while self._read_buffer.qsize():
            self._read_buffer.get(False)

    def flushOutput(self):
        """Clear output buffer, aborting the current output and
        discarding all that is in the buffer."""
        if not self._isOpen: raise portNotOpenError
        self._set_comport_option(PURGE_DATA, PURGE_TRANSMIT_BUFFER)

    def sendBreak(self, duration=0.25):
        """Send break condition. Timed, returns to idle state after given
        duration."""
        if not self._isOpen: raise portNotOpenError
        self.setBreak(True)
        time.sleep(duration)
        self.setBreak(False)

    def setBreak(self, level=True):
        """Set break: Controls TXD. When active, to transmitting is
        possible."""
        if not self._isOpen: raise portNotOpenError
        if level:
            self._set_comport_option(SET_CONTROL, SET_CONTROL_BREAK_ON)
        else:
            self._set_comport_option(SET_CONTROL, SET_CONTROL_BREAK_OFF)

    def setRTS(self, level=True):
        """Set terminal status line: Request To Send"""
        if not self._isOpen: raise portNotOpenError
        if level:
            self._set_comport_option(SET_CONTROL, SET_CONTROL_RTS_ON)
        else:
            self._set_comport_option(SET_CONTROL, SET_CONTROL_RTS_OFF)

    def setDTR(self, level=True):
        """Set terminal status line: Data Terminal Ready"""
        if not self._isOpen: raise portNotOpenError
        if level:
            self._set_comport_option(SET_CONTROL, SET_CONTROL_DTR_ON)
        else:
            self._set_comport_option(SET_CONTROL, SET_CONTROL_DTR_OFF)

    def getCTS(self):
        """Read terminal status line: Clear To Send"""
        if not self._isOpen: raise portNotOpenError
        return bool(self._modemstate & MODEMSTATE_MASK_CTS)

    def getDSR(self):
        """Read terminal status line: Data Set Ready"""
        if not self._isOpen: raise portNotOpenError
        return bool(self._modemstate & MODEMSTATE_MASK_DSR)

    def getRI(self):
        """Read terminal status line: Ring Indicator"""
        if not self._isOpen: raise portNotOpenError
        return bool(self._modemstate & MODEMSTATE_MASK_RI)

    def getCD(self):
        """Read terminal status line: Carrier Detect"""
        if not self._isOpen: raise portNotOpenError
        return bool(self._modemstate & MODEMSTATE_MASK_CD)

    # - - - platform specific - - -
    # None so far

    # - - - RFC2217 specific - - -

    def _read_loop(self):
        """read loop for the socket"""
        M_NORMAL = 0
        M_IAC_SEEN = 1
        M_NEGOTIATE = 2
        mode = M_NORMAL
        suboption = None
        #~ print "XXX reader loop started"
        while self._socket is not None:
            try:
                data = self._socket.recv(1024)
            except (socket.timeout, socket.error):
                data = ''
            if not data:
                # connection closed
                break
                # XXX
            for byte in data:
                #~ print "XXX", ord(byte)
                if mode == M_NORMAL:
                    # interpret as command or as data
                    if byte == IAC:
                        mode = M_IAC_SEEN
                    else:
                        # store data in read buffer or sub option buffer
                        # depending on state
                        if suboption is not None:
                            suboption.append(byte)
                        else:
                            self._read_buffer.put(byte)
                elif mode == M_IAC_SEEN:
                    if byte == IAC:
                        # interpret as command doubled -> insert character
                        # itself
                        self._read_buffer.put(IAC)
                        mode = M_NORMAL
                    elif byte == SB:
                        # sub option start
                        suboption = bytearray()
                        mode = M_NORMAL
                    elif byte == SE:
                        # sub option end -> process it now
                        self._telnet_process_suboption(suboption)
                        suboption = None
                        mode = M_NORMAL
                    elif byte in (DO, DONT, WILL, WONT):
                        # negotiation
                        telnet_command = byte
                        mode = M_NEGOTIATE
                    else:
                        # other telnet commands
                        self._telnet_process_command(byte)
                        mode = M_NORMAL
                elif mode == M_NEGOTIATE: # DO, DONT, WILL, WONT was received, option now following
                    self._telnet_negotiate_option(telnet_command, byte)
                    mode = M_NORMAL
        self._thread = None
        #~ print "XXX reader loop terminated"

    # - incoming telnet commands and options

    def _telnet_process_command(self, command):
        """Process commands other than DO, DONT, WILL, WONT"""
        #~ print "_telnet_process_command %r" % ord(command)

    def _telnet_negotiate_option(self, command, option):
        """Process DO, DONT, WILL, WONT"""
        self._telnet_negotiated_options[option] = command
        #~ print "_telnet_negotiate_option %r %r" % ({DO:'DO', DONT:'DONT', WILL:'WILL', WONT:'WONT'}[command], ord(option))

    def _telnet_process_suboption(self, suboption):
        """Process suboptions, the data between IAC SB and IAC SE"""
        if suboption[0:1] == COM_PORT_OPTION:
            if suboption[1:2] == SERVER_NOTIFY_LINESTATE and len(suboption) >= 3:
                self._linestate = suboption[2] # XXX ensure it is a number
                #~ print "_telnet_process_suboption COM_PORT_OPTION LINESTATE %s %r" % (bin(self._linestate), self._linestate)
            elif suboption[1:2] == SERVER_NOTIFY_MODEMSTATE and len(suboption) >= 3:
                self._modemstate = suboption[2] # XXX ensure it is a number
                #~ print "_telnet_process_suboption COM_PORT_OPTION MODEMSTATE %s %r" % (bin(self._modemstate), self._modemstate)
            else:
                self._rfc2217_negotiated_options[bytes(suboption[1:2])] = bytes(suboption[2:])
                #~ print "_telnet_process_suboption COM_PORT_OPTION %r" % suboption[1:]
        else:
            pass
            #~ print "_telnet_process_suboption unknown %r" % suboption

    # - outgoing telnet commands and options

    def _negotiate_telnet_option(self, action, option):
        """Send DO, DONT, WILL, WONT"""
        #~ print "_negotiate_telnet_option %r %r" % ({DO:'DO', DONT:'DONT', WILL:'WILL', WONT:'WONT'}[action], ord(option))
        #~ if option in self._telnet_negotiated_options and \
                #~ self._telnet_negotioted_options[option] in TELNET_ACTION_SUCCESS_MAP[action]:
            #~ print "_negotiate_telnet_option already in good state"
            #~ return
        self._socket.sendall(to_bytes([IAC, action, option]))
        for tries in range(10):
            if option in self._telnet_negotiated_options and \
                    self._telnet_negotiated_options[option] in TELNET_ACTION_SUCCESS_MAP[action]:
                break
            time.sleep(0.1)
        else:
            raise SerialException("Timeout or server rejected telnet option %r" % (option,))

    def _set_comport_option(self, option, value=[]):
        """Subnegotiation of RFC2217 parameters"""
        #~ print "_set_comport_option %r %r" % (option, value)
        expected_answer = RFC2217_ANSWER_MAP[option]
        if expected_answer in self._rfc2217_negotiated_options: del self._rfc2217_negotiated_options[expected_answer]
        self._socket.sendall(to_bytes([IAC, SB, COM_PORT_OPTION, option] + list(value) + [IAC, SE]))
        if option == SET_CONTROL: 
            time.sleep(0.3)
            return # XXX BAD server hack?
        for tries in range(10):
            if expected_answer in self._rfc2217_negotiated_options and \
                    self._rfc2217_negotiated_options[expected_answer][:len(value)] == value:
                break
            time.sleep(0.1)
        else:
            raise SerialException("Timeout or server rejected RFC2217 option %r %r" % (option, value))


# assemble Serial class with the platform specific implementation and the base
# for file-like behavior. for Python 2.6 and newer, that provide the new I/O
# library, derive from io.RawIOBase
try:
    import io
except ImportError:
    # classic version with our own file-like emulation
    class Serial(RFC2217Serial, FileLike):
        pass
else:
    # io library present
    class Serial(RFC2217Serial, io.RawIOBase):
        pass


# test server: while true; do nc -l -p 7000 -c "sredird debug /dev/ttyUSB0 /var/lock/sredir"; done
if __name__ == '__main__':
    import sys
    s = Serial('rfc2217://localhost:7000', 115200)
    sys.stdout.write('%s\n' % s)

    time.sleep(1.5)
    sys.stdout.write("write...\n")
    s.write("hello\n")
    s.flush()
    time.sleep(2)
    sys.stdout.write("read: %s\n" % s.read(5))

    #~ s.baudrate = 19200
    #~ s.databits = 7
    s.close()
