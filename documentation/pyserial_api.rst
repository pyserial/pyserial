==============
 pySerial API
==============

.. module:: serial

Classes
=======

.. class:: Serial

    .. method:: __init__(port=None, baudrate=9600, bytesize=EIGHTBITS, parity=PARITY_NONE, stopbits=STOPBITS_ONE, timeout=None, xonxoff=0, rtscts=0, interCharTimeout=None)

        :param port:
            Device name or port number number or None.

        :param baudrate:
            Baud rate such as 9600 or 115200 etc.

        :param bytesize:
            Number of data bits. Possible values: FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS

        :param parity:
            Enable parity checking. Possible values: PARITY_NONE PARITY_EVEN PARITY_ODD PARITY_MARK PARITY_SPACE

        :param stopbits:
            Number of stop bits. Possible values: STOPBITS_ONE STOPBITS_ONE_POINT_FIVE STOPBITS_TWO

        :param timeout:
            Set a read timeout value.

        :param xonxoff:
            Enable software flow control.

        :param rtscts:
            Enable hardware (RTS/CTS) flow control.

        :param interCharTimeout:
            Inter-character timeout, None to disable.

        The port is immediately opened on object creation, when a ``port`` is
        given. It is not opened when port is None.

        - Number: number of device, numbering starts at zero.
        - Device name: depending on operating system. e.g. ``/dev/ttyUSB0``
          on GNU/Linux or ``COM3`` on Windows.

        Possible values for the parameter ``timeout``::

                timeout = None  # wait forever
                timeout = 0     # non-blocking mode (return immediately on read)
                timeout = x     # set timeout to x seconds (float allowed)


    .. method:: open()

        Open port.

    .. method:: close()

        Close port immediately.

    .. method:: setBaudrate(baudrate)

        Change baud rate on an open port.

    .. method:: inWaiting()

        Return the number of chars in the receive buffer.

    .. method:: read(size=1)

        Read size bytes from the serial port. If a timeout is set it may return
        less characters as requested. With no timeout it will block until the
        requested number of bytes is read.

    .. method:: write(s)

        Write the string `s` to the port.

    .. method:: flush():

        Flush of file like objects. In this case, wait until all data is
        written.

    .. method:: flushInput()

        Flush input buffer, discarding all it's contents.

    .. method:: flushOutput()

        Clear output buffer, aborting the current output and
        discarding all that is in the buffer.

    .. method:: sendBreak(duration=0.25)

        Send break condition. Timed, returns to idle state after given
        duration.

    .. method:: setBreak(level=True)

        Set break: Controls TXD. When active, no transmitting is possible.

    .. method:: setRTS(level=True)

        Set RTS line to specified logic level.

    .. method:: setDTR(level=True)

        Set DTR line to specified logic level.

    .. method:: getCTS()

        Return the state of the CTS line.

    .. method:: getDSR()

        Return the state of the DSR line.

    .. method:: getRI()

        Return the state of the RI line.

    .. method:: getCD()

        Return the state of the CD line

    Read-only attributes:

    .. attribute:: portstr

        Device name. This is always the device name even if the
        port was opened by a number. (Read Only).

    .. attribute:: BAUDRATES

        A list of valid baud rates. The list may be incomplete such that higher
        baud rates may be supported by the device and that values in between the
        standard baud rates are supported. (Read Only).

    .. attribute:: BYTESIZES

        A list of valid byte sizes for the device (Read Only).

    .. attribute:: PARITIES

        A list of valid parities for the device (Read Only).

    .. attribute:: STOPBITS

        A list of valid stop bit widths for the device (Read Only).


    New values can be assigned to the following attributes, the port will be reconfigured, even if it's opened at that time:

    .. attribute:: port

        Port name/number as set by the user.

    .. attribute:: baudrate

        Current baud rate setting.

    .. attribute:: bytesize

        Byte size in bits.

    .. attribute:: parity

        Parity setting.

    .. attribute:: stopbits

        Stop bit with.

    .. attribute:: timeout

        Timeout setting (seconds, float).

    .. attribute:: xonxoff

        If Xon/Xoff flow control is enabled.

    .. attribute:: rtscts

        If hardware flow control is enabled.

    Platform specific methods.

    .. warning:: Programs using the following methods are not portable to other platforms!

    .. method:: nonblocking()

        :platform: Unix

        Configure the device for nonblocking operations. This can be useful if
        the port is used with ``select``.

    .. method:: fileno()

        :platform: Unix

        Return file descriptor number.


    .. method:: setXON(level=True)

        :platform: Windows

        Set software flow control state.


.. class:: FileLike

    .. method:: readline()

    An abstract file like class. It is used as base class for :class:`Serial`.

    This class implements readline and readlines based on read and
    writelines based on write.
    This class is used to provide the above functions for to Serial
    port objects.

    Note that when the serial port was opened with _NO_ timeout that
    readline blocks until it sees a newline (or the specified size is
    reached) and that readlines would never return and therefore
    refuses to work (it raises an exception in this case)!

    .. method:: readline(size=None, eol='\n')

        :param size: Max number of  bytes to read, ``None`` -> no limit.
        :param eol: The end of line character.

        Read a line which is terminated with end-of-line (eol) character
        ('\n' by default) or until timeout.

    .. method:: readlines(sizehint=None, eol='\n')

        :param size: Ignored parameter.
        :param eol: The end of line character.

        Read a list of lines, until timeout. ``sizehint`` is ignored and only
        present for API compatibility with built-in File objects.

    .. method:: xreadlines(sizehint=None)

        Just calls ``readlines`` - here for compatibility.

    .. method:: writelines(sequence)

        Write a list of strings to the port.

    .. method:: flush()

        Flush of file like objects. It's a no-op in this class, may be overridden.

    .. method:: read()

        Raises NotImplementedError, needs to be overridden by subclass.

    .. method:: write()

        Raises NotImplementedError, needs to be overridden by subclass.


    To be able to use the file like object as iterator for e.g. 
    ``for line in Serial(0): ...`` usage:

    .. method:: next()

        Return the next line by calling :meth:`readline`.

    .. method:: __iter__()

        Returns self.


.. class:: SerialBase

    The following attributes are implemented as properties. They work with open
    and closed ports.

    .. attribute:: port

        Read or write port. When the port is already open, it will be closed
        and reopened with the new setting.

    .. attribute:: baudrate

        Read or write current baud rate setting. It is possible to change this
        on an opened port.

    .. attribute:: bytesize

        Read or write current data byte size setting. It is possible to change
        this on an opened port.

    .. attribute:: parity

        Read or write current parity setting. It is possible to change this on
        an opened port.

    .. attribute:: stopbits

        Read or write current stop bit width setting. It is possible to change
        this on an opened port.

    .. attribute:: timeout

        Read or write current read timeout setting. It is possible to change
        this on an opened port.

    .. attribute:: writeTimeout

        Read or write current write timeout setting. It is possible to change
        this on an opened port.

    .. attribute:: xonxoff

        Read or write current software flow control rate setting. It is
        possible to change this on an opened port.

    .. attribute:: rtscts

        Read or write current hardware flow control setting. It is possible to
        change this on an opened port.

    .. attribute:: dsrdtr

        Read or write current hardware flow control setting. It is possible to
        change this on an opened port.

    .. attribute:: interCharTimeout

        Read or write current inter character timeout setting. It is possible
        to change this on an opened port.

    The following constants are also provided:

    .. attribute:: BAUDRATES

        A tuple of standard baud rate values. The actual device may support more
        or less...

    .. attribute:: BYTESIZES

        A tuple of supported byte size values.

    .. attribute:: PARITIES

        A tuple of supported parity settings.

    .. attribute:: STOPBITS

        A tuple of supported stop bit settings.



Exceptions
==========

.. exception:: SerialException

    Base class for serial port exceptions.

.. exception:: SerialTimeoutException

    Exception that is raised on write timeouts.


Constants
=========

Parity
------
.. data:: PARITY_NONE
.. data:: PARITY_EVEN
.. data:: PARITY_ODD
.. data:: PARITY_MARK
.. data:: PARITY_SPACE

Stopbits
--------
.. data:: STOPBITS_ONE
.. data:: STOPBITS_ONE_POINT_FIVE
.. data:: STOPBITS_TWO

Bytesize
--------
.. data:: FIVEBITS
.. data:: SIXBITS
.. data:: SEVENBITS
.. data:: EIGHTBITS

Others
-------
.. data:: XON
.. data:: XOFF
