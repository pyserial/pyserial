#! python
# Python Serial Port Extension for Win32, Linux, BSD, Jython
# see __init__.py
#
# (C) 2001-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

import io

# ``memoryview`` was introduced in Python 2.7 and ``bytes(some_memoryview)``
# isn't returning the contents (very unfortunate). Therefore we need special
# cases and test for it. Ensure that there is a ``memoryview`` object for older
# Python versions. This is easier than making every test dependent on its
# existence.
try:
    memoryview
except (NameError, AttributeError):
    # implementation does not matter as we do not realy use it.
    # it just must not inherit from something else we might care for.
    class memoryview(object):
        pass


# "for byte in data" fails for python3 as it returns ints instead of bytes
def iterbytes(b):
    """Iterate over bytes, returning bytes instead of ints (python3)"""
    x = 0
    while True:
        a = b[x:x+1]
        x += 1
        if a:
            yield a
        else:
            break

# all Python versions prior 3.x convert ``str([17])`` to '[17]' instead of '\x11'
# so a simple ``bytes(sequence)`` doesn't work for all versions
def to_bytes(seq):
    """convert a sequence to a bytes type"""
    if isinstance(seq, bytes):
        return seq
    elif isinstance(seq, bytearray):
        return bytes(seq)
    elif isinstance(seq, memoryview):
        return seq.tobytes()
    else:
        b = bytearray()
        for item in seq:
            # this one handles int and bytes in Python 2.7
            # add conversion in case of Python 3.x
            if isinstance(item, bytes):
                item = ord(item)
            b.append(item)
        return bytes(b)

# create control bytes
XON  = to_bytes([17])
XOFF = to_bytes([19])

CR = to_bytes([13])
LF = to_bytes([10])


PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE = 'N', 'E', 'O', 'M', 'S'
STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO = (1, 1.5, 2)
FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS = (5, 6, 7, 8)

PARITY_NAMES = {
    PARITY_NONE:  'None',
    PARITY_EVEN:  'Even',
    PARITY_ODD:   'Odd',
    PARITY_MARK:  'Mark',
    PARITY_SPACE: 'Space',
}


class SerialException(IOError):
    """Base class for serial port related exceptions."""


class SerialTimeoutException(SerialException):
    """Write timeouts give an exception"""


writeTimeoutError = SerialTimeoutException('Write timeout')
portNotOpenError = SerialException('Attempting to use a port that is not open')


class SerialBase(io.RawIOBase):
    """\
    Serial port base class. Provides __init__ function and properties to
    get/set port settings.
    """

    # default values, may be overridden in subclasses that do not support all values
    BAUDRATES = (50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800,
                 9600, 19200, 38400, 57600, 115200, 230400, 460800, 500000,
                 576000, 921600, 1000000, 1152000, 1500000, 2000000, 2500000,
                 3000000, 3500000, 4000000)
    BYTESIZES = (FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS)
    PARITIES  = (PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE)
    STOPBITS  = (STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO)

    def __init__(self,
                 port = None,           # number of device, numbering starts at
                                        # zero. if everything fails, the user
                                        # can specify a device string, note
                                        # that this isn't portable anymore
                                        # port will be opened if one is specified
                 baudrate=9600,         # baud rate
                 bytesize=EIGHTBITS,    # number of data bits
                 parity=PARITY_NONE,    # enable parity checking
                 stopbits=STOPBITS_ONE, # number of stop bits
                 timeout=None,          # set a timeout value, None to wait forever
                 xonxoff=False,         # enable software flow control
                 rtscts=False,          # enable RTS/CTS flow control
                 writeTimeout=None,     # set a timeout for writes
                 dsrdtr=False,          # None: use rtscts setting, dsrdtr override if True or False
                 interCharTimeout=None  # Inter-character timeout, None to disable
                 ):
        """\
        Initialize comm port object. If a port is given, then the port will be
        opened immediately. Otherwise a Serial port object in closed state
        is returned.
        """

        self._isOpen   = False
        self._port     = None           # correct value is assigned below through properties
        self._baudrate = None           # correct value is assigned below through properties
        self._bytesize = None           # correct value is assigned below through properties
        self._parity   = None           # correct value is assigned below through properties
        self._stopbits = None           # correct value is assigned below through properties
        self._timeout  = None           # correct value is assigned below through properties
        self._writeTimeout = None       # correct value is assigned below through properties
        self._xonxoff  = None           # correct value is assigned below through properties
        self._rtscts   = None           # correct value is assigned below through properties
        self._dsrdtr   = None           # correct value is assigned below through properties
        self._interCharTimeout = None   # correct value is assigned below through properties
        self._rs485_mode = None         # disabled by default

        # assign values using get/set methods using the properties feature
        self.port     = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity   = parity
        self.stopbits = stopbits
        self.timeout  = timeout
        self.writeTimeout = writeTimeout
        self.xonxoff  = xonxoff
        self.rtscts   = rtscts
        self.dsrdtr   = dsrdtr
        self.interCharTimeout = interCharTimeout

        if port is not None:
            self.open()

    def isOpen(self):
        """Check if the port is opened."""
        return self._isOpen


    #  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -

    @property
    def port(self):
        """\
        Get the current port setting. The value that was passed on init or using
        setPort() is passed back. See also the attribute portstr which contains
        the name of the port as a string.
        """
        return self._port

    @port.setter
    def port(self, port):
        """\
        Change the port. The attribute portstr is set to a string that
        contains the name of the port.
        """

        was_open = self._isOpen
        if was_open: self.close()
        self.portstr = port
        self._port = port
        self.name = self.portstr
        if was_open: self.open()


    @property
    def baudrate(self):
        """Get the current baud rate setting."""
        return self._baudrate

    @baudrate.setter
    def baudrate(self, baudrate):
        """\
        Change baud rate. It raises a ValueError if the port is open and the
        baud rate is not possible. If the port is closed, then the value is
        accepted and the exception is raised when the port is opened.
        """
        try:
            b = int(baudrate)
        except TypeError:
            raise ValueError("Not a valid baudrate: %r" % (baudrate,))
        else:
            if b <= 0:
                raise ValueError("Not a valid baudrate: %r" % (baudrate,))
            self._baudrate = b
            if self._isOpen:  self._reconfigurePort()


    @property
    def bytesize(self):
        """Get the current byte size setting."""
        return self._bytesize

    @bytesize.setter
    def bytesize(self, bytesize):
        """Change byte size."""
        if bytesize not in self.BYTESIZES: raise ValueError("Not a valid byte size: %r" % (bytesize,))
        self._bytesize = bytesize
        if self._isOpen: self._reconfigurePort()



    @property
    def parity(self):
        """Get the current parity setting."""
        return self._parity

    @parity.setter
    def parity(self, parity):
        """Change parity setting."""
        if parity not in self.PARITIES: raise ValueError("Not a valid parity: %r" % (parity,))
        self._parity = parity
        if self._isOpen: self._reconfigurePort()



    @property
    def stopbits(self):
        """Get the current stop bits setting."""
        return self._stopbits

    @stopbits.setter
    def stopbits(self, stopbits):
        """Change stop bits size."""
        if stopbits not in self.STOPBITS: raise ValueError("Not a valid stop bit size: %r" % (stopbits,))
        self._stopbits = stopbits
        if self._isOpen: self._reconfigurePort()


    @property
    def timeout(self):
        """Get the current timeout setting."""
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        """Change timeout setting."""
        if timeout is not None:
            try:
                timeout + 1     # test if it's a number, will throw a TypeError if not...
            except TypeError:
                raise ValueError("Not a valid timeout: %r" % (timeout,))
            if timeout < 0: raise ValueError("Not a valid timeout: %r" % (timeout,))
        self._timeout = timeout
        if self._isOpen: self._reconfigurePort()


    @property
    def writeTimeout(self):
        """Get the current timeout setting."""
        return self._writeTimeout

    @writeTimeout.setter
    def writeTimeout(self, timeout):
        """Change timeout setting."""
        if timeout is not None:
            if timeout < 0: raise ValueError("Not a valid timeout: %r" % (timeout,))
            try:
                timeout + 1     #test if it's a number, will throw a TypeError if not...
            except TypeError:
                raise ValueError("Not a valid timeout: %r" % timeout)

        self._writeTimeout = timeout
        if self._isOpen: self._reconfigurePort()


    @property
    def xonxoff(self):
        """Get the current XON/XOFF setting."""
        return self._xonxoff

    @xonxoff.setter
    def xonxoff(self, xonxoff):
        """Change XON/XOFF setting."""
        self._xonxoff = xonxoff
        if self._isOpen: self._reconfigurePort()


    @property
    def rtscts(self):
        """Get the current RTS/CTS flow control setting."""
        return self._rtscts

    @rtscts.setter
    def rtscts(self, rtscts):
        """Change RTS/CTS flow control setting."""
        self._rtscts = rtscts
        if self._isOpen: self._reconfigurePort()


    @property
    def dsrdtr(self):
        """Get the current DSR/DTR flow control setting."""
        return self._dsrdtr

    @dsrdtr.setter
    def dsrdtr(self, dsrdtr=None):
        """Change DsrDtr flow control setting."""
        if dsrdtr is None:
            # if not set, keep backwards compatibility and follow rtscts setting
            self._dsrdtr = self._rtscts
        else:
            # if defined independently, follow its value
            self._dsrdtr = dsrdtr
        if self._isOpen: self._reconfigurePort()


    @property
    def interCharTimeout(self):
        """Get the current inter-character timeout setting."""
        return self._interCharTimeout

    @interCharTimeout.setter
    def interCharTimeout(self, interCharTimeout):
        """Change inter-character timeout setting."""
        if interCharTimeout is not None:
            if interCharTimeout < 0: raise ValueError("Not a valid timeout: %r" % interCharTimeout)
            try:
                interCharTimeout + 1     # test if it's a number, will throw a TypeError if not...
            except TypeError:
                raise ValueError("Not a valid timeout: %r" % interCharTimeout)

        self._interCharTimeout = interCharTimeout
        if self._isOpen: self._reconfigurePort()


    #  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    # functions useful for RS-485 adapters

    @property
    def rs485_mode(self):
        """\
        Enable RS485 mode and apply new settings, set to None to disable.
        See serial.rs485.RS485Settings for more info about the value.
        """
        return self._rs485_mode

    @rs485_mode.setter
    def rs485_mode(self, rs485_settings):
        self._rs485_mode = rs485_settings
        if self._isOpen: self._reconfigurePort()

    #  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -

    _SETTINGS = ('baudrate', 'bytesize', 'parity', 'stopbits', 'xonxoff',
            'dsrdtr', 'rtscts', 'timeout', 'writeTimeout', 'interCharTimeout')

    def getSettingsDict(self):
        """\
        Get current port settings as a dictionary. For use with
        applySettingsDict.
        """
        return dict([(key, getattr(self, '_'+key)) for key in self._SETTINGS])

    def applySettingsDict(self, d):
        """\
        apply stored settings from a dictionary returned from
        getSettingsDict. it's allowed to delete keys from the dictionary. these
        values will simply left unchanged.
        """
        for key in self._SETTINGS:
            if key in d and d[key] != getattr(self, '_'+key):   # check against internal "_" value
                setattr(self, key, d[key])          # set non "_" value to use properties write function

    #  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -

    def __repr__(self):
        """String representation of the current port settings and its state."""
        return "%s<id=0x%x, open=%s>(port=%r, baudrate=%r, bytesize=%r, parity=%r, stopbits=%r, timeout=%r, xonxoff=%r, rtscts=%r, dsrdtr=%r)" % (
            self.__class__.__name__,
            id(self),
            self._isOpen,
            self.portstr,
            self.baudrate,
            self.bytesize,
            self.parity,
            self.stopbits,
            self.timeout,
            self.xonxoff,
            self.rtscts,
            self.dsrdtr,
        )


    #  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    # compatibility with io library

    def readable(self): return True
    def writable(self): return True
    def seekable(self): return False
    def readinto(self, b):
        data = self.read(len(b))
        n = len(data)
        try:
            b[:n] = data
        except TypeError as err:
            import array
            if not isinstance(b, array.array):
                raise err
            b[:n] = array.array('b', data)
        return n

    #  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    # context manager

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    #  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    # additional functionality

    def read_until(self, terminator=LF, size=None):
        """\
        Read until a termination sequence is found ('\n' by default), the size
        is exceeded or until timeout occurs.
        """
        lenterm = len(terminator)
        line = bytearray()
        while True:
            c = self.read(1)
            if c:
                line += c
                if line[-lenterm:] == terminator:
                    break
                if size is not None and len(line) >= size:
                    break
            else:
                break
        return bytes(line)


    def iread_until(self, *args, **kwargs):
        """\
        Read lines, implemented as generator. It will raise StopIteration on
        timeout (empty read).
        """
        while True:
            line = self.read_until(*args, **kwargs)
            if not line: break
            yield line


#  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
if __name__ == '__main__':
    import sys
    s = SerialBase()
    sys.stdout.write('port name:  %s\n' % s.name)
    sys.stdout.write('baud rates: %s\n' % s.BAUDRATES)
    sys.stdout.write('byte sizes: %s\n' % s.BYTESIZES)
    sys.stdout.write('parities:   %s\n' % s.PARITIES)
    sys.stdout.write('stop bits:  %s\n' % s.STOPBITS)
    sys.stdout.write('%s\n' % s)
