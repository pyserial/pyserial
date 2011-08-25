==============
 pySerial API
==============

.. module:: serial

Classes
=======

Native ports
------------

.. class:: Serial

    .. method:: __init__(port=None, baudrate=9600, bytesize=EIGHTBITS, parity=PARITY_NONE, stopbits=STOPBITS_ONE, timeout=None, xonxoff=False, rtscts=False, writeTimeout=None, dsrdtr=False, interCharTimeout=None)

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
            :const:`PARITY_NONE`, :const:`PARITY_EVEN`, :const:`PARITY_ODD`
            :const:`PARITY_MARK`, :const:`PARITY_SPACE`

        :param stopbits:
            Number of stop bits. Possible values:
            :const:`STOPBITS_ONE`, :const:`STOPBITS_ONE_POINT_FIVE`,
            :const:`STOPBITS_TWO`

        :param timeout:
            Set a read timeout value.

        :param xonxoff:
            Enable software flow control.

        :param rtscts:
            Enable hardware (RTS/CTS) flow control.

        :param dsrdtr:
            Enable hardware (DSR/DTR) flow control.

        :param writeTimeout:
            Set a write timeout value.

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

        The parameter *baudrate* can be one of the standard values:
        50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800,
        9600, 19200, 38400, 57600, 115200.
        These are well supported on all platforms. Standard values above 115200
        such as: 230400, 460800, 500000, 576000, 921600, 1000000, 1152000,
        1500000, 2000000, 2500000, 3000000, 3500000, 4000000 also work on many
        platforms.

        Non-standard values are also supported on some platforms (GNU/Linux, MAC
        OSX >= Tiger, Windows). Though, even on these platforms some serial
        ports may reject non-standard values.

        Possible values for the parameter *timeout*:

        - ``timeout = None``:  wait forever
        - ``timeout = 0``:     non-blocking mode (return immediately on read)
        - ``timeout = x``:     set timeout to ``x`` seconds (float allowed)

        Writes are blocking by default, unless *writeTimeout* is set. For
        possible values refer to the list for *timeout* above.

        Note that enabling both flow control methods (*xonxoff* and *rtscts*)
        together may not be supported. It is common to use one of the methods
        at once, not both.

        *dsrdtr* is not supported by all platforms (silently ignored). Setting
        it to ``None`` has the effect that its state follows *rtscts*.

        Also consider using the function :func:`serial_for_url` instead of
        creating Serial instances directly.

        .. versionchanged:: 2.5
            *dsrdtr* now defaults to ``False`` (instead of *None*)

    .. method:: open()

        Open port.

    .. method:: close()

        Close port immediately.

    .. method:: __del__()

        Destructor, close port when serial port instance is freed.


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
            and newer) and :class:`str` otherwise.

    .. method:: write(data)

        :param data: Data to send.
        :return: Number of bytes written.
        :exception SerialTimeoutException:
            In case a write timeout is configured for the port and the time is
            exceeded.

        Write the string *data* to the port.

        .. versionchanged:: 2.5
            Accepts instances of :class:`bytes` and :class:`bytearray` when
            available (Python 2.6 and newer) and :class:`str` otherwise.

        .. versionchanged:: 2.5
            Write returned ``None`` in previous versions.

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

    New values can be assigned to the following attributes (properties), the
    port will be reconfigured, even if it's opened at that time:


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

        A list of valid baud rates. The list may be incomplete such that higher
        baud rates may be supported by the device and that values in between the
        standard baud rates are supported. (Read Only).

    .. attribute:: BYTESIZES

        A list of valid byte sizes for the device (Read Only).

    .. attribute:: PARITIES

        A list of valid parities for the device (Read Only).

    .. attribute:: STOPBITS

        A list of valid stop bit widths for the device (Read Only).


    The following methods are for compatibility with the :mod:`io` library.

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

        :param b: bytearray or array instance
        :return: Number of byte read

        Read up to len(b) bytes into :class:`bytearray` *b* and return the
        number of bytes read.

        .. versionadded:: 2.5

    The port settings can be read and written as dictionary.

    .. method:: getSettingsDict()

        :return: a dictionary with current port settings.

        Get a dictionary with port settings. This is useful to backup the
        current settings so that a later point in time they can be restored
        using :meth:`applySettingsDict`.

        Note that control lines (RTS/DTR) are part of the settings.

        .. versionadded:: 2.5

    .. method:: applySettingsDict(d)

        :param d: a dictionary with port settings.

        Applies a dictionary that was created by :meth:`getSettingsDict`. Only
        changes are applied and when a key is missing it means that the setting
        stays unchanged.

        Note that control lines (RTS/DTR) are not changed.

        .. versionadded:: 2.5

    Platform specific methods.

    .. warning:: Programs using the following methods are not portable to other platforms!

    .. method:: nonblocking()

        :platform: Unix

        Configure the device for nonblocking operation. This can be useful if
        the port is used with :mod:`select`.

    .. method:: fileno()

        :platform: Unix
        :return: File descriptor.

        Return file descriptor number for the port that is opened by this object.
        It is useful when serial ports are used with :mod:`select`.

    .. method:: setXON(level=True)

        :platform: Windows
        :param level: Set flow control state.

        Set software flow control state.

.. note::

    For systems that provide the :py:mod:`io` library (Python 2.6 and newer), the
    class :class:`Serial` will derive from :py:class:`io.RawIOBase`. For all
    others from :class:`FileLike`.

Implementation detail: some attributes and functions are provided by the
class :class:`SerialBase` and some by the platform specific class and
others by the base class mentioned above.

.. class:: FileLike

    An abstract file like class. It is used as base class for :class:`Serial`
    when no :py:mod:`io` module is available.

    This class implements :meth:`readline` and :meth:`readlines` based on
    :meth:`read` and :meth:`writelines` based on :meth:`write`.

    Note that when the serial port was opened with no timeout, that
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

    Other high level access functions.

    .. method:: readline(size=None, eol='\\n')

        :param size: Max number of bytes to read, ``None`` -> no limit.
        :param eol: The end of line character.

        Read a line which is terminated with end-of-line (*eol*) character
        (``\n`` by default) or until timeout.

    .. method:: readlines(sizehint=None, eol='\\n')

        :param sizehint: Ignored parameter.
        :param eol: The end of line character.

        Read a list of lines, until timeout. *sizehint* is ignored and only
        present for API compatibility with built-in File objects.

        Note that this function only returns on a timeout.

    .. method:: xreadlines(sizehint=None)

        Read lines, implemented as generator. Unlike *readlines* (that only
        returns on a timeout) is this function yielding lines as they are
        received.

        .. deprecated:: 2.5
            Use ``for line in Serial(...): ...`` instead. This method is not
            available in Python 2.6 and newer where the :mod:`io` library is
            available and pySerial bases on it.

        .. versionchanged:: 2.5
            Implement as generator.


:rfc:`2217` Network ports
-------------------------

.. warning:: This implementation is currently in an experimental state. Use
    at your own risk.

.. class:: rfc2217.Serial

    This implements a :rfc:`2217` compatible client. Port names are URLs_ in the
    form: ``rfc2217://<host>:<port>[/<option>[/<option>]]``

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

    - :rfc:`2217` flow control between client and server (objects internal
      buffer may eat all your memory when never read).
    - No authentication support (servers may not prompt for a password etc.)
    - No encryption.

    Due to lack of authentication and encryption it is not suitable to use this
    client for connections across the internet and should only be used in
    controlled environments.

    .. versionadded:: 2.5


.. class:: rfc2217.PortManager

    This class provides helper functions for implementing :rfc:`2217`
    compatible servers.

    Basically, it implements every thing needed for the :rfc:`2217` protocol.
    It just does not open sockets and read/write to serial ports (though it
    changes other port settings). The user of this class must take care of the
    data transmission itself. The reason for that is, that this way, this class
    supports all programming models such as threads and select.

    Usage examples can be found in the examples where two TCP/IP - serial
    converters are shown, one using threads (the single port server) and an
    other using select (the multi port server).

    .. note:: Each new client connection must create a new instance as this
              object (and the :rfc:`2217` protocol) has internal state.

    .. method:: __init__(serial_port, connection, debug_output=False)

        :param serial_port: a :class:`Serial` instance that is managed.
        :param connection: an object implementing :meth:`write`, used to write
            to the network.
        :param debug_output: enables debug messages: a :class:`logging.Logger`
            instance or None.

        Initializes the Manager and starts negotiating with client in Telnet
        and :rfc:`2217` protocol. The negotiation starts immediately so that
        the class should be instantiated in the moment the client connects.

        The *serial_port* can be controlled by :rfc:`2217` commands. This
        object will modify the port settings (baud rate etc.) and control lines
        (RTS/DTR) send BREAK etc. when the corresponding commands are found by
        the :meth:`filter` method.

        The *connection* object must implement a :meth:`write(data)` function.
        This function must ensure that *data* is written at once (no user data
        mixed in, i.e. it must be thread-safe). All data must be sent in its
        raw form (:meth:`escape` must not be used) as it is used to send Telnet
        and :rfc:`2217` control commands.

        For diagnostics of the connection or the implementation, *debug_output*
        can be set to an instance of a :class:`logging.Logger` (e.g.
        ``logging.getLogger('rfc2217.server')``). The caller should configure
        the logger using ``setLevel`` for the desired detail level of the logs.

    .. method:: escape(data)

        :param data: data to be sent over the network.
        :return: data, escaped for Telnet/:rfc:`2217`

        A generator that escapes all data to be compatible with :rfc:`2217`.
        Implementors of servers should use this function to process all data
        sent over the network.

        The function returns a generator which can be used in ``for`` loops.
        It can be converted to bytes using :func:`serial.to_bytes`.

    .. method:: filter(data)

        :param data: data read from the network, including Telnet and
            :rfc:`2217` controls.
        :return: data, free from Telnet and :rfc:`2217` controls.

        A generator that filters and processes all data related to :rfc:`2217`.
        Implementors of servers should use this function to process all data
        received from the network.

        The function returns a generator which can be used in ``for`` loops.
        It can be converted to bytes using :func:`serial.to_bytes`.

    .. method:: check_modem_lines(force_notification=False)

        :param force_notification: Set to false. Parameter is for internal use.

        This function needs to be called periodically (e.g. every second) when
        the server wants to send NOTIFY_MODEMSTATE messages. This is required
        to support the client for reading CTS/DSR/RI/CD status lines.

        The function reads the status line and issues the notifications
        automatically.

    .. versionadded:: 2.5

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

*Parity*

.. data:: PARITY_NONE
.. data:: PARITY_EVEN
.. data:: PARITY_ODD
.. data:: PARITY_MARK
.. data:: PARITY_SPACE

*Stop bits*

.. data:: STOPBITS_ONE
.. data:: STOPBITS_ONE_POINT_FIVE
.. data:: STOPBITS_TWO

Note that 1.5 stop bits are not supported on POSIX. It will fall back to 2 stop
bits.

*Byte size*

.. data:: FIVEBITS
.. data:: SIXBITS
.. data:: SEVENBITS
.. data:: EIGHTBITS


*Others*

Default control characters (instances of :class:`bytes` for Python 3.0+) for
software flow control:

.. data:: XON
.. data:: XOFF

Module version:

.. data:: VERSION

    A string indicating the pySerial version, such as ``2.5``.

    .. versionadded:: 2.3


Module functions and attributes
===============================

.. function:: device(number)

    :param number: Port number.
    :return: String containing device name.
    :deprecated: Use device names directly.

    Convert a port number to a platform dependent device name. Unfortunately
    this does not work well for all platforms; e.g. some may miss USB-Serial
    converters and enumerate only internal serial ports.

    The conversion may be made off-line, that is, there is no guarantee that
    the returned device name really exists on the system.


.. function:: serial_for_url(url, \*args, \*\*kwargs)

    :param url: Device name, number or :ref:`URL <URLs>`
    :param do_not_open: When set to true, the serial port is not opened.
    :return: an instance of :class:`Serial` or a compatible object.

    Get a native or a :rfc:`2217` implementation of the Serial class, depending
    on port/url. This factory function is useful when an application wants
    to support both, local ports and remote ports. There is also support
    for other types, see :ref:`URL <URLs>` section below.

    The port is not opened when a keyword parameter called *do_not_open* is
    given and true, by default it is opened.

    .. versionadded:: 2.5


.. attribute:: protocol_handler_packages

    This attribute is a list of package names (strings) that is searched for
    protocol handlers.

    e.g. we want to support a URL ``foobar://``. A module
    ``my_handlers.protocol_foobar`` is provided by the user::

        serial.protocol_handler_packages.append("my_handlers")
        s = serial.serial_for_url("foobar://")

    For an URL starting with ``XY://`` is the function :func:`serial_for_url`
    attempts to import ``PACKAGE.protocol_XY`` with each candidate for
    ``PACKAGE`` from this list.

    .. versionadded:: 2.6


.. function:: to_bytes(sequence)

    :param sequence: String or list of integers
    :returns: an instance of ``bytes``

    Convert a sequence to a ``bytes`` type. This is used to write code that is
    compatible to Python 2.x and 3.x.

    In Python versions prior 3.x, ``bytes`` is a subclass of str. They convert
    ``str([17])`` to ``'[17]'`` instead of ``'\x11'`` so a simple
    ``bytes(sequence)`` doesn't work for all versions of Python.

    This function is used internally and in the unit tests.

    .. versionadded:: 2.5


.. _URLs:

URLs
----
The function :func:`serial_for_url` accepts the following types of URLs:

- ``rfc2217://<host>:<port>[/<option>[/<option>]]``
- ``socket://<host>:<port>[/<option>[/<option>]]``
- ``loop://[<option>[/<option>]]``

Device names are also supported, e.g.:

- ``/dev/ttyUSB0`` (Linux)
- ``COM3`` (Windows)

Future releases of pySerial might add more types. Since pySerial 2.6 it is also
possible for the user to add protocol handlers using
:attr:`protocol_handler_packages`.

``rfc2217://``
    Used to connect to :rfc:`2217` compatible servers. All serial port
    functions are supported. Implemented by :class:`rfc2217.Serial`.

    Supported options in the URL are:

    - ``ign_set_control`` does not wait for acknowledges to SET_CONTROL. This
      option can be used for non compliant servers (i.e. when getting an
      ``remote rejected value for option 'control'`` error when connecting).

    - ``poll_modem``: The client issues NOTIFY_MODEMSTATE requests when status
      lines are read (CTS/DTR/RI/CD). Without this option it relies on the server
      sending the notifications automatically (that's what the RFC suggests and
      most servers do). Enable this option when :meth:`getCTS` does not work as
      expected, i.e. for servers that do not send notifications.

    - ``timeout=<value>``: Change network timeout (default 3 seconds). This is
      useful when the server takes a little more time to send its answers. The
      timeout applies to the initial Telnet / :rfc:`2271` negotiation as well
      as changing port settings or control line change commands.

    - ``logging=[debug|info|warning|error]``: Prints diagnostic messages (not
      useful for end users). It uses the logging module and a logger called
      ``pySerial.rfc2217`` so that the application can setup up logging
      handlers etc. It will call :meth:`logging.basicConfig` which initializes
      for output on ``sys.stderr`` (if no logging was set up already).

``socket://``
    The purpose of this connection type is that applications using pySerial can
    connect to TCP/IP to serial port converters that do not support :rfc:`2217`.

    Uses a TCP/IP socket. All serial port settings, control and status lines
    are ignored. Only data is transmitted and received.

    Supported options in the URL are:

    - ``logging=[debug|info|warning|error]``: Prints diagnostic messages (not
      useful for end users). It uses the logging module and a logger called
      ``pySerial.socket`` so that the application can setup up logging handlers
      etc. It will call :meth:`logging.basicConfig` which initializes for
      output on ``sys.stderr`` (if no logging was set up already).

``loop://``
    The least useful type. It simulates a loop back connection
    (``RX<->TX``  ``RTS<->CTS``  ``DTR<->DSR``). It could be used to test
    applications or run the unit tests.

    Supported options in the URL are:

    - ``logging=[debug|info|warning|error]``: Prints diagnostic messages (not
      useful for end users). It uses the logging module and a logger called
      ``pySerial.loop`` so that the application can setup up logging handlers
      etc. It will call :meth:`logging.basicConfig` which initializes for
      output on ``sys.stderr`` (if no logging was set up already).


Examples:

- ``rfc2217://localhost:7000``
- ``rfc2217://localhost:7000/poll_modem``
- ``rfc2217://localhost:7000/ign_set_control/timeout=5.5``
- ``socket://localhost:7777``
- ``loop://logging=debug``

Tools
=====


serial.tools.list_ports
-----------------------
.. module:: serial.tools.list_ports
.. versionadded:: 2.6

This module can be executed to get a list of ports (``python -m
serial.tools.list_ports``). It also contains the following functions.


.. function:: comports()

    :return: an iterable.

    The function returns an iterable that yields tuples of three strings:

    - port name as it can be passed to :class:`serial.Serial` or
      :func:`serial.serial_for_url`
    - description in human readable form
    - sort of hardware ID. E.g. may contain VID:PID of USB-serial adapters.

    Items are returned in no particular order. It may make sense to sort the
    items. Also note that the reported strings are different across platforms
    and operating systems, even for the same device.

    .. note:: Support is limited to a number of operating systems. On some
              systems description and hardware ID will not be available
              (``None``).

    :platform: Posix (/dev files)
    :platform: Linux (/dev files, sysfs and lsusb)
    :platform: Windows (setupapi, registry)


.. function:: grep(regexp)

    :param regexp: regular expression (see stdlib :mod:`re`)
    :return: filtered sequence, see :func:`comports`.

    Search for ports using a regular expression. Port name, description and
    hardware ID are searched (case insensitive). The function returns an
    iterable that contains the same tuples that :func:`comport` generates but
    only those that match the regexp.


serial.tools.miniterm
-----------------------
.. module:: serial.tools.miniterm
.. versionadded:: 2.6

Miniterm is now available as module instead of example.
see :ref:`miniterm` for details.

