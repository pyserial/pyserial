==============
 pySerial API
==============

.. module:: serial

Classes
=======

.. class:: Serial

    .. method:: __init__(port=None, baudrate=9600, bytesize=EIGHTBITS, parity=PARITY_NONE, stopbits=STOPBITS_ONE, timeout=None, xonxoff=0, rtscts=0, interCharTimeout=None)

        :param port:
            Device name or port number number or :const:`None`.

        :param baudrate:
            Baud rate such as 9600 or 115200 etc.

        :param bytesize:
            Number of data bits. Possible values:
            :const:`FIVEBITS`, :const:`SIXBITS`, :const:`SEVENBITS`,
            :const:`EIGHTBITS`

        :param parity:
            Enable parity checking. Possible values:
            :const:`PARITY_NONE` :const:`PARITY_EVEN` :const:`PARITY_ODD`
            :const:`PARITY_MARK` :const:`PARITY_SPACE`

        :param stopbits:
            Number of stop bits. Possible values:
            :const:`STOPBITS_ONE` :const:`STOPBITS_ONE_POINT_FIVE`
            :const:`STOPBITS_TWO`

        :param timeout:
            Set a read timeout value.

        :param xonxoff:
            Enable software flow control.

        :param rtscts:
            Enable hardware (RTS/CTS) flow control.

        :param interCharTimeout:
            Inter-character timeout, :const:`None` to disable (default).

        :exception ValueError:
            Will be raised when parameter are out of range, e.g. baud rate, data bits.

        :exception SerialException:
            In case the device can not be found or can not be configured.


        The port is immediately opened on object creation, when a *port* is
        given. It is not opened when *port* is :const:`None` and a successive call
        to :meth:`open` will be needed.

        Possible values for the parameter *port*:

        - Number: number of device, numbering starts at zero.
        - Device name: depending on operating system. e.g. ``/dev/ttyUSB0``
          on GNU/Linux or ``COM3`` on Windows.

        Possible values for the parameter *timeout*:

        - ``timeout = None``:  wait forever
        - ``timeout = 0``:     non-blocking mode (return immediately on read)
        - ``timeout = x``:     set timeout to ``x`` seconds (float allowed)


    .. method:: open()

        Open port.

    .. method:: close()

        Close port immediately.


    The following methods may raise :exc:`ValueError` when applied to a closed
    port.

    .. method:: read(size=1)

        :param size: Number of bytes to read.
        :return: Bytes read from the port.

        Read *size* bytes from the serial port. If a timeout is set it may
        return less characters as requested. With no timeout it will block
        until the requested number of bytes is read.

        .. versionchanged:: 2.5
            Returns an instance of :class:`bytes` when available (Python 2.6
            and newer) and :class:`str` otherwiese.

    .. method:: write(data)

        :param data: Data to send.
        :return: Number of bytes written.
        :exception SerialTimeoutException:
            In case a write timeout is configured for the port and the time is
            exceeded.

        Write the string *data* to the port.

        .. versionchanged:: 2.5
            Accepts instances of :class:`bytes` and :class:`bytearray` when
            available (Python 2.6 and newer) and :class:`str` otherwiese.

    .. method:: inWaiting()

        Return the number of chars in the receive buffer.

    .. method:: flush()

        Flush of file like objects. In this case, wait until all data is
        written.

    .. method:: flushInput()

        Flush input buffer, discarding all it's contents.

    .. method:: flushOutput()

        Clear output buffer, aborting the current output and
        discarding all that is in the buffer.

    .. method:: sendBreak(duration=0.25)

        :param duration: Time (float) to activate the BREAK condition.

        Send break condition. Timed, returns to idle state after given
        duration.

    .. method:: setBreak(level=True)

        :param level: when true activate BREAK condition, else disable.

        Set break: Controls TXD. When active, no transmitting is possible.

    .. method:: setRTS(level=True)

        :param level: Set control line to logic level.

        Set RTS line to specified logic level.

    .. method:: setDTR(level=True)

        :param level: Set control line to logic level.

        Set DTR line to specified logic level.

    .. method:: getCTS()

        :return: Current state (boolean)

        Return the state of the CTS line.

    .. method:: getDSR()

        :return: Current state (boolean)

        Return the state of the DSR line.

    .. method:: getRI()

        :return: Current state (boolean)

        Return the state of the RI line.

    .. method:: getCD()

        :return: Current state (boolean)

        Return the state of the CD line

    Read-only attributes:

    .. attribute:: name

        Device name. This is always the device name even if the
        port was opened by a number. (Read Only).

        .. versionadded:: 2.5

    .. attribute:: portstr

        :deprecated: use :attr:`name` instead

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


    New values can be assigned to the following attributes, the port will be
    reconfigured, even if it's opened at that time:

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
        :return: File descriptor.

        Return file descriptor number for the port that is opened by this object.

    .. method:: setXON(level=True)

        :platform: Windows
        :param level: Set flow control state.

        Set software flow control state.


.. class:: SerialBase

    The following attributes are implemented as properties. They work with open
    and closed ports.

    .. attribute:: port

        Read or write port. When the port is already open, it will be closed
        and reopened with the new setting.

    .. attribute:: baudrate

        Read or write current baud rate setting.

    .. attribute:: bytesize

        Read or write current data byte size setting.

    .. attribute:: parity

        Read or write current parity setting.

    .. attribute:: stopbits

        Read or write current stop bit width setting.

    .. attribute:: timeout

        Read or write current read timeout setting.

    .. attribute:: writeTimeout

        Read or write current write timeout setting.

    .. attribute:: xonxoff

        Read or write current software flow control rate setting.

    .. attribute:: rtscts

        Read or write current hardware flow control setting.

    .. attribute:: dsrdtr

        Read or write current hardware flow control setting.

    .. attribute:: interCharTimeout

        Read or write current inter character timeout setting.

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

    .. method:: readline(size=None, eol='\\n')

        :param size: Max number of bytes to read, ``None`` -> no limit.
        :param eol: The end of line character.

        Read a line which is terminated with end-of-line (*eol*) character
        (``\\n`` by default) or until timeout.

    .. method:: readlines(sizehint=None, eol='\\n')

        :param size: Ignored parameter.
        :param eol: The end of line character.

        Read a list of lines, until timeout. *sizehint* is ignored and only
        present for API compatibility with built-in File objects.

    .. method:: xreadlines(sizehint=None)

        Just calls :meth:`readlines` - here for compatibility.

    For compatibility with the :mod:`io` library are the following methods.

    .. method:: readable()

        :return: True
        .. versionadded:: 2.5

    .. method:: writable()

        :return: True
        .. versionadded:: 2.5

    .. method:: seekable()

        :return: False
        .. versionadded:: 2.5

    .. method:: readinto(b)

        :param b: bytearray or array instace
        :return: Number of byte read

        Read up to len(b) bytes into bytearray b and return the number of bytes read.

        .. versionadded:: 2.5

 
.. note::

    For systems that provide the :mod:`io` library (Python 2.6 and newer), the
    class :class:`Serial` will derrive from :class:`io.RawIOBase`. For all
    others from :class:`FileLike`.

.. class:: FileLike

    An abstract file like class. It is used as base class for :class:`Serial`.

    This class implements :meth:`readline` and :meth:`readlines` based on read
    and :meth:`writelines` based on write.  This class is used to provide the
    above functions for to Serial port objects.

    Note that when the serial port was opened with no timeout that
    :meth:`readline` blocks until it sees a newline (or the specified size is
    reached) and that :meth:`readlines` would never return and therefore
    refuses to work (it raises an exception in this case)!

    .. method:: writelines(sequence)

        Write a list of strings to the port.


    The following three methods are overridden in :class:`Serial`.

    .. method:: flush()

        Flush of file like objects. It's a no-op in this class, may be overridden.

    .. method:: read()

        Raises NotImplementedError, needs to be overridden by subclass.

    .. method:: write(data)

        Raises NotImplementedError, needs to be overridden by subclass.

    The following functions are implemented for compatibility with other
    file-like objects, however serial ports are not seekable.


    .. method:: seek(pos, whence=0)

        :exception IOError: always, as method is not supported on serial port

        .. versionadded:: 2.5

    .. method:: tell()

        :exception IOError: always, as method is not supported on serial port

        .. versionadded:: 2.5

    .. method:: truncate(self, n=None)

        :exception IOError: always, as method is not supported on serial port

        .. versionadded:: 2.5

    .. method:: isatty()

        :exception IOError: always, as method is not supported on serial port

        .. versionadded:: 2.5

    To be able to use the file like object as iterator for e.g. 
    ``for line in Serial(0): ...`` usage:

    .. method:: next()

        Return the next line by calling :meth:`readline`.

    .. method:: __iter__()

        Returns self.


.. class:: rfc2217.Serial

    This implements a :rfc:`2217` compatible client. Port names are URLs in the
    form: ``rfc2217://<host>:<port>``

    .. warning:: This implementation is currently in an experimental state. Use
        at your own risk.

    This class API is compatible to :class:`Serial` with a few exceptions:

    - numbers as port name are not allowed, only URLs in the form described
      above.
    - writeTimeout is not implemented
    - The current implementation starts a thread that keeps reading from the
      (internal) socket. The thread is managed automatically by the
      :class:`rfc2217.Serial` port object on :meth:`open`/:meth:`close`.
      However it may be a problem for user applications that like to use select
      instead of threads.

    Due to the nature of the network and protocol involved there are a few
    extra points to keep in mind:

    - All operations have an additional latency time.
    - Setting control lines (RTS/CTS) needs more time.
    - Reading the status lines (DSR/DTR etc.) returns a cached value. When that
      cache is updated depends entirely on the server. The server itself may
      implement a polling at a certain rate and quick changes may be invisible.
    - The network layer also has buffers. This means that :meth:`flush`,
      :meth:`flushInput` and :meth:`flushOutput` may work with additional delay.
      Likewise :meth:`inWaiting` returns the size of the data arrived at the
      object internal buffer and excludes any bytes in the network buffers or
      any server side buffer.
    - Closing and immediately reopening the same port may fail due to time
      needed by the server to get ready again.

    Not implemented yet / Possible problems with the implementation:

    - :rfc:`2217` flow control between client and server. (objects internal
      buffer may eat all your memory when never read)
    - The telnet option negotiation may be done incorrectly.


.. seealso::

   :rfc:`2217` - Telnet Com Port Control Option



Exceptions
==========

.. exception:: SerialException

    Base class for serial port exceptions.

    .. versionchanged:: 2.5
        Now derrives from :exc:`IOError` instead of :exc:`Exception`

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

Stop bits
---------
.. data:: STOPBITS_ONE
.. data:: STOPBITS_ONE_POINT_FIVE
.. data:: STOPBITS_TWO

Byte size
---------
.. data:: FIVEBITS
.. data:: SIXBITS
.. data:: SEVENBITS
.. data:: EIGHTBITS

Others
-------
Default control characters (instnces of :class:`bytes` for Python 3.0+) for
software flow control:

.. data:: XON
.. data:: XOFF

Module version:

.. data:: VERSION

    A string indicating the pySerial version, such as ``2.5``.

Functions:

.. function:: device(number)

    :param number: Port number.
    :return: String containing device name.
    :deprecated: Use device names directly.

    Convert a port number to a platform dependent device name. Unfortunately
    this does not work well for all platforms; e.g. some may miss USB-Serial
    converters and enumerate only internal serial ports.

    The conversion may be made off-line, that is, there is no guarantee that
    the returned device name really exists on the system.
