====================
 Short introduction
====================

Opening serial ports
====================

Open port 0 at "9600,8,N,1", no timeout::

    >>> import serial
    >>> ser = serial.Serial(0)  # open first serial port
    >>> print ser.portstr       # check which port was really used
    >>> ser.write("hello")      # write a string
    >>> ser.close()             # close port

Open named port at "19200,8,N,1", 1s timeout::

    >>> ser = serial.Serial('/dev/ttyS1', 19200, timeout=1)
    >>> x = ser.read()          # read one byte
    >>> s = ser.read(10)        # read up to ten bytes (timeout)
    >>> line = ser.readline()   # read a '\n' terminated line
    >>> ser.close()

Open second port at "38400,8,E,1", non blocking HW handshaking::

    >>> ser = serial.Serial(1, 38400, timeout=0,
    ...                     parity=serial.PARITY_EVEN, rtscts=1)
    >>> s = ser.read(100)       # read up to one hundred bytes
    ...                         # or as much is in the buffer

Configuring ports later
=======================

Get a Serial instance and configure/open it later::

    >>> ser = serial.Serial()
    >>> ser.baudrate = 19200
    >>> ser.port = 0
    >>> ser
    Serial<id=0xa81c10, open=False>(port='COM1', baudrate=19200, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=0, rtscts=0)
    >>> ser.open()
    >>> ser.isOpen()
    True
    >>> ser.close()
    >>> ser.isOpen()
    False

Readline
========
Be carefully when using "readline". Do specify a timeout when opening the
serial port otherwise it could block forever if no newline character is
received. Also note that "readlines" only works with a timeout. "readlines"
depends on having a timeout and interprets that as EOF (end of file). It raises
an exception if the port is not opened correctly.

Do also have a look at the example files in the examples directory in the
source distribution or online.
