==============
 pySerial API
==============

.. module:: serial

Classes
=======

Native ports
------------

.. class:: Serial

    .. method:: __init__(port=None, baudrate=9600, bytesize=EIGHTBITS, parity=PARITY_NONE, stopbits=STOPBITS_ONE, timeout=None, xonxoff=False, rtscts=False, write_timeout=None, dsrdtr=False, inter_byte_timeout=None, exclusive=None)

        :param port:
            Device name or :const:`None`.

        :param int baudrate:
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

        :param float timeout:
            Set a read timeout value in seconds.

        :param bool xonxoff:
            Enable software flow control.

        :param bool rtscts:
            Enable hardware (RTS/CTS) flow control.

        :param bool dsrdtr:
            Enable hardware (DSR/DTR) flow control.

        :param float write_timeout:
            Set a write timeout value in seconds.

        :param float inter_byte_timeout:
            Inter-character timeout, :const:`None` to disable (default).

        :param bool exclusive:
            Set exclusive access mode (POSIX only).  A port cannot be opened in 
            exclusive access mode if it is already open in exclusive access mode.

        :exception ValueError:
            Will be raised when parameter are out of range, e.g. baud rate, data bits.

        :exception SerialException:
            In case the device can not be found or can not be configured.


        The port is immediately opened on object creation, when a *port* is
        given. It is not opened when *port* is :const:`None` and a successive call
        to :meth:`open` is required.

        *port* is a device name: depending on operating system. e.g.
        ``/dev/ttyUSB0`` on GNU/Linux or ``COM3`` on Windows.

        The parameter *baudrate* can be one of the standard values:
        50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800,
        9600, 19200, 38400, 57600, 115200.
        These are well supported on all platforms.

        Standard values above 115200, such as: 230400, 460800, 500000, 576000,
        921600, 1000000, 1152000, 1500000, 2000000, 2500000, 3000000, 3500000,
        4000000 also work on many platforms and devices.

        Non-standard values are also supported on some platforms (GNU/Linux, MAC
        OSX >= Tiger, Windows). Though, even on these platforms some serial
        ports may reject non-standard values.

        Possible values for the parameter *timeout* which controls the behavior
        of :meth:`read`:

        - ``timeout = None``:  wait forever / until requested number of bytes
          are received
        - ``timeout = 0``:     non-blocking mode, return immediately in any case,
          returning zero or more, up to the requested number of bytes
        - ``timeout = x``:     set timeout to ``x`` seconds (float allowed)
          returns immediately when the requested number of bytes are available,
          otherwise wait until the timeout expires and return all bytes that
          were received until then.

        :meth:`write` is blocking by default, unless *write_timeout* is set.
        For possible values refer to the list for *timeout* above.

        Note that enabling both flow control methods (*xonxoff* and *rtscts*)
        together may not be supported. It is common to use one of the methods
        at once, not both.

        *dsrdtr* is not supported by all platforms (silently ignored). Setting
        it to ``None`` has the effect that its state follows *rtscts*.

        Also consider using the function :func:`serial_for_url` instead of
        creating Serial instances directly.

        .. versionchanged:: 2.5
            *dsrdtr* now defaults to ``False`` (instead of *None*)
        .. versionchanged:: 3.0 numbers as *port* argument are no longer supported
        .. versionadded:: 3.3 ``exclusive`` flag

    .. method:: open()

        Open port. The state of :attr:`rts` and :attr:`dtr` is applied.

        .. note::

            Some OS and/or drivers may activate RTS and or DTR automatically,
            as soon as the port is opened. There may be a glitch on RTS/DTR
            when :attr:`rts` or :attr:`dtr` are set differently from their
            default value (``True`` / active).

        .. note::

            For compatibility reasons, no error is reported when applying
            :attr:`rts` or :attr:`dtr` fails on POSIX due to EINVAL (22) or
            ENOTTY (25).

    .. method:: close()

        Close port immediately.

    .. method:: __del__()

        Destructor, close port when serial port instance is freed.


    The following methods may raise :exc:`SerialException` when applied to a closed
    port.

    .. method:: read(size=1)

        :param size: Number of bytes to read.
        :return: Bytes read from the port.
        :rtype: bytes

        Read *size* bytes from the serial port. If a timeout is set it may
        return less characters as requested. With no timeout it will block
        until the requested number of bytes is read.

        .. versionchanged:: 2.5
            Returns an instance of :class:`bytes` when available (Python 2.6
            and newer) and :class:`str` otherwise.

    .. method:: read_until(expected=LF, size=None)

        :param expected: The byte string to search for.
        :param size: Number of bytes to read.
        :return: Bytes read from the port.
        :rtype: bytes

        Read until an expected sequence is found ('\\n' by default), the size
        is exceeded or until timeout occurs. If a timeout is set it may
        return less characters as requested. With no timeout it will block
        until the requested number of bytes is read.

        .. versionchanged:: 2.5
            Returns an instance of :class:`bytes` when available (Python 2.6
            and newer) and :class:`str` otherwise.

    .. method:: write(data)

        :param data: Data to send.
        :return: Number of bytes written.
        :rtype: int
        :exception SerialTimeoutException:
            In case a write timeout is configured for the port and the time is
            exceeded.

        Write the bytes *data* to the port. This should be of type ``bytes``
        (or compatible such as ``bytearray`` or ``memoryview``). Unicode
        strings must be encoded (e.g. ``'hello'.encode('utf-8'``).

    .. versionchanged:: 2.5
            Accepts instances of :class:`bytes` and :class:`bytearray` when
            available (Python 2.6 and newer) and :class:`str` otherwise.

        .. versionchanged:: 2.5
            Write returned ``None`` in previous versions.

    .. method:: flush()

        Flush of file like objects. In this case, wait until all data is
        written.

    .. attribute:: in_waiting

        :getter: Get the number of bytes in the input buffer
        :type: int

        Return the number of bytes in the receive buffer.

        .. versionchanged:: 3.0 changed to property from ``inWaiting()``

    .. attribute:: out_waiting

        :getter: Get the number of bytes in the output buffer
        :type: int
        :platform: Posix
        :platform: Windows

        Return the number of bytes in the output buffer.

        .. versionchanged:: 2.7 (Posix support added)
        .. versionchanged:: 3.0 changed to property from ``outWaiting()``

    .. method:: reset_input_buffer()

        Flush input buffer, discarding all its contents.

        .. versionchanged:: 3.0 renamed from ``flushInput()``

    .. method:: reset_output_buffer()

        Clear output buffer, aborting the current output and
        discarding all that is in the buffer.

        Note, for some USB serial adapters, this may only flush the buffer of
        the OS and not all the data that may be present in the USB part.

        .. versionchanged:: 3.0 renamed from ``flushOutput()``

    .. method:: send_break(duration=0.25)

        :param float duration: Time in seconds, to activate the BREAK condition.

        Send break condition. Timed, returns to idle state after given
        duration.


    .. attribute:: break_condition

        :getter: Get the current BREAK state
        :setter: Control the BREAK state
        :type: bool

        When set to ``True`` activate BREAK condition, else disable.
        Controls TXD. When active, no transmitting is possible.

    .. attribute:: rts

        :setter: Set the state of the RTS line
        :getter: Return the state of the RTS line
        :type: bool

        Set RTS line to specified logic level. It is possible to assign this
        value before opening the serial port, then the value is applied upon
        :meth:`open` (with restrictions, see :meth:`open`).

    .. attribute:: dtr

        :setter: Set the state of the DTR line
        :getter: Return the state of the DTR line
        :type: bool

        Set DTR line to specified logic level. It is possible to assign this
        value before opening the serial port, then the value is applied upon
        :meth:`open` (with restrictions, see :meth:`open`).

    Read-only attributes:

    .. attribute:: name

        :getter: Device name.
        :type: str

        .. versionadded:: 2.5

    .. attribute:: cts

        :getter: Get the state of the CTS line
        :type: bool

        Return the state of the CTS line.

    .. attribute:: dsr

        :getter: Get the state of the DSR line
        :type: bool

        Return the state of the DSR line.

    .. attribute:: ri

        :getter: Get the state of the RI line
        :type: bool

        Return the state of the RI line.

    .. attribute:: cd

        :getter: Get the state of the CD line
        :type: bool

        Return the state of the CD line

    .. attribute:: is_open

        :getter: Get the state of the serial port, whether it's open.
        :type: bool

    New values can be assigned to the following attributes (properties), the
    port will be reconfigured, even if it's opened at that time:


    .. attribute:: port

        :type: str

        Read or write port. When the port is already open, it will be closed
        and reopened with the new setting.

    .. attribute:: baudrate

        :getter: Get current baud rate
        :setter: Set new baud rate
        :type: int

        Read or write current baud rate setting.

    .. attribute:: bytesize

        :getter: Get current byte size
        :setter: Set new byte size. Possible values:
            :const:`FIVEBITS`, :const:`SIXBITS`, :const:`SEVENBITS`,
            :const:`EIGHTBITS`
        :type: int

        Read or write current data byte size setting.

    .. attribute:: parity

        :getter: Get current parity setting
        :setter: Set new parity mode. Possible values:
            :const:`PARITY_NONE`, :const:`PARITY_EVEN`, :const:`PARITY_ODD`
            :const:`PARITY_MARK`, :const:`PARITY_SPACE`

        Read or write current parity setting.

    .. attribute:: stopbits

        :getter: Get current stop bit setting
        :setter: Set new stop bit setting. Possible values:
            :const:`STOPBITS_ONE`, :const:`STOPBITS_ONE_POINT_FIVE`,
            :const:`STOPBITS_TWO`

        Read or write current stop bit width setting.

    .. attribute:: timeout

        :getter: Get current read timeout setting
        :setter: Set read timeout
        :type: float (seconds)

        Read or write current read timeout setting.

    .. attribute:: write_timeout

        :getter: Get current write timeout setting
        :setter: Set write timeout
        :type: float (seconds)

        Read or write current write timeout setting.

        .. versionchanged:: 3.0 renamed from ``writeTimeout``

    .. attribute:: inter_byte_timeout

        :getter: Get current inter byte timeout setting
        :setter: Disable (``None``) or enable the inter byte timeout
        :type: float or None

        Read or write current inter byte timeout setting.

        .. versionchanged:: 3.0 renamed from ``interCharTimeout``

    .. attribute:: xonxoff

        :getter: Get current software flow control setting
        :setter: Enable or disable software flow control
        :type: bool

        Read or write current software flow control rate setting.

    .. attribute:: rtscts

        :getter: Get current hardware flow control setting
        :setter: Enable or disable hardware flow control
        :type: bool

        Read or write current hardware flow control setting.

    .. attribute:: dsrdtr

        :getter: Get current hardware flow control setting
        :setter: Enable or disable hardware flow control
        :type: bool

        Read or write current hardware flow control setting.

    .. attribute:: rs485_mode

        :getter: Get the current RS485 settings
        :setter: Disable (``None``) or enable the RS485 settings
        :type: :class:`rs485.RS485Settings` or ``None``
        :platform: Posix (Linux, limited set of hardware)
        :platform: Windows (only RTS on TX possible)

        Attribute to configure RS485 support. When set to an instance of
        :class:`rs485.RS485Settings` and supported by OS, RTS will be active
        when data is sent and inactive otherwise (for reception). The
        :class:`rs485.RS485Settings` class provides additional settings
        supported on some platforms.

        .. versionadded:: 3.0


    The following constants are also provided:

    .. attribute:: BAUDRATES

        A list of valid baud rates. The list may be incomplete, such that higher
        and/or intermediate baud rates may also be supported by the device
        (Read Only).

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

    .. method:: readline(size=-1)

        Provided via :meth:`io.IOBase.readline`

    .. method:: readlines(hint=-1)

        Provided via :meth:`io.IOBase.readlines`

    .. method:: writelines(lines)

        Provided via :meth:`io.IOBase.writelines`

    The port settings can be read and written as dictionary. The following
    keys are supported: ``write_timeout``, ``inter_byte_timeout``,
    ``dsrdtr``, ``baudrate``, ``timeout``, ``parity``, ``bytesize``,
    ``rtscts``, ``stopbits``, ``xonxoff``

    .. method:: get_settings()

        :return: a dictionary with current port settings.
        :rtype: dict

        Get a dictionary with port settings. This is useful to backup the
        current settings so that a later point in time they can be restored
        using :meth:`apply_settings`.

        Note that the state of control lines (RTS/DTR) are not part of the
        settings.

        .. versionadded:: 2.5
        .. versionchanged:: 3.0 renamed from ``getSettingsDict``

    .. method:: apply_settings(d)

        :param dict d: a dictionary with port settings.

        Applies a dictionary that was created by :meth:`get_settings`. Only
        changes are applied and when a key is missing, it means that the
        setting stays unchanged.

        Note that control lines (RTS/DTR) are not changed.

        .. versionadded:: 2.5
        .. versionchanged:: 3.0 renamed from ``applySettingsDict``


    .. _context-manager:

    This class can be used as context manager. The serial port is closed when
    the context is left.

    .. method:: __enter__()

        :returns: Serial instance

        Returns the instance that was used in the ``with`` statement.

        Example:

        >>> with serial.serial_for_url(port) as s:
        ...     s.write(b'hello')

        The port is opened automatically:

        >>> port = serial.Serial()
        >>> port.port = '...'
        >>> with port as s:
        ...     s.write(b'hello')

        Which also means that ``with`` statements can be used repeatedly,
        each time opening and closing the port.

        .. versionchanged:: 3.4 the port is automatically opened


    .. method:: __exit__(exc_type, exc_val, exc_tb)

        Closes serial port (exceptions are not handled by ``__exit__``).


    Platform specific methods.

    .. warning:: Programs using the following methods and attributes are not
                 portable to other platforms!

    .. method:: nonblocking()

        :platform: Posix

        .. deprecated:: 3.2
           The serial port is already opened in this mode. This method is not
           needed and going away.


    .. method:: fileno()

        :platform: Posix
        :return: File descriptor.

        Return file descriptor number for the port that is opened by this object.
        It is useful when serial ports are used with :mod:`select`.

    .. method:: set_input_flow_control(enable)

        :platform: Posix
        :param bool enable: Set flow control state.

        Manually control flow - when software flow control is enabled.

        This will send XON (true) and XOFF (false) to the other device.

        .. versionadded:: 2.7 (Posix support added)
        .. versionchanged:: 3.0 renamed from ``flowControlOut``

    .. method:: set_output_flow_control(enable)

        :platform: Posix (HW and SW flow control)
        :platform: Windows (SW flow control only)
        :param bool enable: Set flow control state.

        Manually control flow of outgoing data - when hardware or software flow
        control is enabled.

        Sending will be suspended when called with ``False`` and enabled when
        called with ``True``.

        .. versionchanged:: 2.7 (renamed on Posix, function was called ``flowControl``)
        .. versionchanged:: 3.0 renamed from ``setXON``

    .. method:: cancel_read()

        :platform: Posix
        :platform: Windows

        Cancel a pending read operation from another thread. A blocking
        :meth:`read` call is aborted immediately. :meth:`read` will not report
        any error but return all data received up to that point (similar to a
        timeout).

        On Posix a call to `cancel_read()` may cancel a future :meth:`read` call.

        .. versionadded:: 3.1

    .. method:: cancel_write()

        :platform: Posix
        :platform: Windows

        Cancel a pending write operation from another thread. The
        :meth:`write` method will return immediately (no error indicated).
        However the OS may still be sending from the buffer, a separate call to
        :meth:`reset_output_buffer` may be needed.

        On Posix a call to `cancel_write()` may cancel a future :meth:`write` call.

        .. versionadded:: 3.1

    .. note:: The following members are deprecated and will be removed in a
              future release.

    .. attribute:: portstr

        .. deprecated:: 2.5 use :attr:`name` instead

    .. method:: inWaiting()

        .. deprecated:: 3.0 see :attr:`in_waiting`

    .. method:: isOpen()

        .. deprecated:: 3.0 see :attr:`is_open`

    .. attribute:: writeTimeout

        .. deprecated:: 3.0 see :attr:`write_timeout`

    .. attribute:: interCharTimeout

        .. deprecated:: 3.0 see :attr:`inter_byte_timeout`

    .. method:: sendBreak(duration=0.25)

        .. deprecated:: 3.0 see :meth:`send_break`

    .. method:: flushInput()

        .. deprecated:: 3.0 see :meth:`reset_input_buffer`

    .. method:: flushOutput()

        .. deprecated:: 3.0 see :meth:`reset_output_buffer`

    .. method:: setBreak(level=True)

        .. deprecated:: 3.0 see :attr:`break_condition`

    .. method:: setRTS(level=True)

        .. deprecated:: 3.0 see :attr:`rts`

    .. method:: setDTR(level=True)

        .. deprecated:: 3.0 see :attr:`dtr`

    .. method:: getCTS()

        .. deprecated:: 3.0 see :attr:`cts`

    .. method:: getDSR()

        .. deprecated:: 3.0 see :attr:`dsr`

    .. method:: getRI()

        .. deprecated:: 3.0 see :attr:`ri`

    .. method:: getCD()

        .. deprecated:: 3.0 see :attr:`cd`

    .. method:: getSettingsDict()

        .. deprecated:: 3.0 see :meth:`get_settings`

    .. method:: applySettingsDict(d)

        .. deprecated:: 3.0 see :meth:`apply_settings`

    .. method:: outWaiting()

        .. deprecated:: 3.0 see :attr:`out_waiting`

    .. method:: setXON(level=True)

        .. deprecated:: 3.0 see :meth:`set_output_flow_control`

    .. method:: flowControlOut(enable)

        .. deprecated:: 3.0 see :meth:`set_input_flow_control`

    .. attribute:: rtsToggle

        :platform: Windows

        Attribute to configure RTS toggle control setting. When enabled and
        supported by OS, RTS will be active when data is available and inactive
        if no data is available.

        .. versionadded:: 2.6
        .. versionchanged:: 3.0 (removed, see :attr:`rs485_mode` instead)


Implementation detail: some attributes and functions are provided by the
class :class:`serial.SerialBase` which inherits from :class:`io.RawIOBase`
and some by the platform specific class and others by the base class
mentioned above.


RS485 support
-------------
The :class:`Serial` class has a :attr:`Serial.rs485_mode` attribute which allows to
enable RS485 specific support on some platforms. Currently Windows and Linux
(only a small number of devices) are supported.

:attr:`Serial.rs485_mode` needs to be set to an instance of
:class:`rs485.RS485Settings` to enable or to ``None`` to disable this feature.

Usage::

    import serial
    import serial.rs485
    ser = serial.Serial(...)
    ser.rs485_mode = serial.rs485.RS485Settings(...)
    ser.write(b'hello')

There is a subclass :class:`rs485.RS485` available to emulate the RS485 support
on regular serial ports (``serial.rs485`` needs to be imported).


.. class:: rs485.RS485Settings

    A class that holds RS485 specific settings which are supported on
    some platforms.

    .. versionadded:: 3.0

    .. method:: __init__(rts_level_for_tx=True, rts_level_for_rx=False, loopback=False, delay_before_tx=None, delay_before_rx=None):

        :param bool rts_level_for_tx:
            RTS level for transmission

        :param bool rts_level_for_rx:
            RTS level for reception

        :param bool loopback:
            When set to ``True`` transmitted data is also received.

        :param float delay_before_tx:
            Delay after setting RTS but before transmission starts

        :param float delay_before_rx:
            Delay after transmission ends and resetting RTS

    .. attribute:: rts_level_for_tx

            RTS level for transmission.

    .. attribute:: rts_level_for_rx

            RTS level for reception.

    .. attribute:: loopback

            When set to ``True`` transmitted data is also received.

    .. attribute:: delay_before_tx

            Delay after setting RTS but before transmission starts (seconds as float).

    .. attribute:: delay_before_rx

            Delay after transmission ends and resetting RTS (seconds as float).


.. class:: rs485.RS485

    A subclass that replaces the :meth:`Serial.write` method with one that toggles RTS
    according to the RS485 settings.

    Usage::

        ser = serial.rs485.RS485(...)
        ser.rs485_mode = serial.rs485.RS485Settings(...)
        ser.write(b'hello')

    .. warning:: This may work unreliably on some serial ports (control signals not
        synchronized or delayed compared to data). Using delays may be unreliable
        (varying times, larger than expected) as the OS may not support very fine
        grained delays (no smaller than in the order of tens of milliseconds).

    .. note:: Some implementations support this natively in the class
        :class:`Serial`. Better performance can be expected when the native version
        is used.

    .. note:: The loopback property is ignored by this implementation. The actual
        behavior depends on the used hardware.



:rfc:`2217` Network ports
-------------------------

.. warning:: This implementation is currently in an experimental state. Use
    at your own risk.

.. class:: rfc2217.Serial

    This implements a :rfc:`2217` compatible client. Port names are :ref:`URL
    <URLs>` in the form: ``rfc2217://<host>:<port>[?<option>[&<option>]]``

    This class API is compatible to :class:`Serial` with a few exceptions:

    - ``write_timeout`` is not implemented
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
      :meth:`reset_input_buffer` and :meth:`reset_output_buffer` may work with
      additional delay.  Likewise :attr:`in_waiting` returns the size of the
      data arrived at the objects internal buffer and excludes any bytes in the
      network buffers or any server side buffer.
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

    Basically, it implements everything needed for the :rfc:`2217` protocol.
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

        The *connection* object must implement a :meth:`write` function.
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
        Now derives from :exc:`IOError` instead of :exc:`Exception`

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

    A string indicating the pySerial version, such as ``3.0``.

    .. versionadded:: 2.3


Module functions and attributes
===============================

.. function:: device(number)

    .. versionchanged:: 3.0 removed, use ``serial.tools.list_ports`` instead


.. function:: serial_for_url(url, \*args, \*\*kwargs)

    :param url: Device name, number or :ref:`URL <URLs>`
    :param do_not_open: When set to true, the serial port is not opened.
    :return: an instance of :class:`Serial` or a compatible object.

    Get a native or a :rfc:`2217` implementation of the Serial class, depending
    on port/url. This factory function is useful when an application wants
    to support both, local ports and remote ports. There is also support
    for other types, see :ref:`URL <URLs>` section.

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

    :param sequence: bytes, bytearray or memoryview
    :returns: an instance of ``bytes``

    Convert a sequence to a ``bytes`` type. This is used to write code that is
    compatible to Python 2.x and 3.x.

    In Python versions prior 3.x, ``bytes`` is a subclass of str. They convert
    ``str([17])`` to ``'[17]'`` instead of ``'\x11'`` so a simple
    ``bytes(sequence)`` doesn't work for all versions of Python.

    This function is used internally and in the unit tests.

    .. versionadded:: 2.5

.. function:: iterbytes(sequence)

    :param sequence: bytes, bytearray or memoryview
    :returns: a generator that yields bytes

    Some versions of Python (3.x) would return integers instead of bytes when
    looping over an instance of ``bytes``. This helper function ensures that
    bytes are returned.

    .. versionadded:: 3.0


Threading
=========

.. module:: serial.threaded
.. versionadded:: 3.0

.. warning:: This implementation is currently in an experimental state. Use
    at your own risk.

This module provides classes to simplify working with threads and protocols.

.. class::  Protocol

    Protocol as used by the :class:`ReaderThread`. This base class provides empty
    implementations of all methods.


    .. method:: connection_made(transport)

        :param transport: instance used to write to serial port.

        Called when reader thread is started.

    .. method:: data_received(data)

        :param bytes data: received bytes

        Called with snippets received from the serial port.

    .. method:: connection_lost(exc)

        :param exc: Exception if connection was terminated by error else ``None``

        Called when the serial port is closed or the reader loop terminated
        otherwise.

.. class:: Packetizer(Protocol)

    Read binary packets from serial port. Packets are expected to be terminated
    with a ``TERMINATOR`` byte (null byte by default).

    The class also keeps track of the transport.

    .. attribute:: TERMINATOR = b'\\0'

    .. method:: __init__()

    .. method:: connection_made(transport)

        Stores transport.

    .. method:: connection_lost(exc)

        Forgets transport.

    .. method:: data_received(data)

        :param bytes data: partial received data

        Buffer received data and search for :attr:`TERMINATOR`, when found,
        call :meth:`handle_packet`.

    .. method:: handle_packet(packet)

        :param bytes packet: a packet as defined by ``TERMINATOR``

        Process packets - to be overridden by subclassing.


.. class:: LineReader(Packetizer)

    Read and write (Unicode) lines from/to serial port.
    The encoding is applied.


    .. attribute:: TERMINATOR = b'\\r\\n'

        Line ending.

    .. attribute:: ENCODING = 'utf-8'

        Encoding of the send and received data.

    .. attribute:: UNICODE_HANDLING = 'replace'

        Unicode error handly policy.

    .. method:: handle_packet(packet)

        :param bytes packet: a packet as defined by ``TERMINATOR``

        In this case it will be a line, calls :meth:`handle_line` after applying
        the :attr:`ENCODING`.

    .. method:: handle_line(line)

        :param str line: Unicode string with one line (excluding line terminator)

        Process one line - to be overridden by subclassing.

    .. method:: write_line(text)

        :param str text: Unicode string with one line (excluding line terminator)

        Write *text* to the transport. *text* is expected to be a Unicode
        string and the encoding is applied before sending and also the
        :attr:`TERMINATOR` (new line) is appended.


.. class:: ReaderThread(threading.Thread)

    Implement a serial port read loop and dispatch to a Protocol instance (like
    the :class:`asyncio.Protocol`) but do it with threads.

    Calls to :meth:`close` will close the serial port but it is also possible
    to just :meth:`stop` this thread and continue to use the serial port
    instance otherwise.

    .. method:: __init__(serial_instance, protocol_factory)

        :param serial_instance: serial port instance (opened) to be used.
        :param protocol_factory: a callable that returns a Protocol instance

        Initialize thread.

        Note that the ``serial_instance`` 's timeout is set to one second!
        Other settings are not changed.

    .. method:: stop()

        Stop the reader thread.

    .. method:: run()

        The actual reader loop driven by the thread. It calls
        :meth:`Protocol.connection_made`, reads from the serial port calling
        :meth:`Protocol.data_received` and finally calls :meth:`Protocol.connection_lost`
        when :meth:`close` is called or an error occurs.

    .. method:: write(data)

        :param bytes data: data to write

        Thread safe writing (uses lock).

    .. method:: close()

        Close the serial port and exit reader thread, calls :meth:`stop` (uses lock).

    .. method:: connect()

        Wait until connection is set up and return the transport and protocol
        instances.


    This class can be used as context manager, in this case it starts
    the thread and connects automatically. The serial port is closed
    when the context is left.

    .. method:: __enter__()

        :returns: protocol

        Connect and return protocol instance.

    .. method:: __exit__(exc_type, exc_val, exc_tb)

        Closes serial port.

Example::

    class PrintLines(LineReader):
        def connection_made(self, transport):
            super(PrintLines, self).connection_made(transport)
            sys.stdout.write('port opened\n')
            self.write_line('hello world')

        def handle_line(self, data):
            sys.stdout.write('line received: {}\n'.format(repr(data)))

        def connection_lost(self, exc):
            if exc:
                traceback.print_exc(exc)
            sys.stdout.write('port closed\n')

    ser = serial.serial_for_url('loop://', baudrate=115200, timeout=1)
    with ReaderThread(ser, PrintLines) as protocol:
        protocol.write_line('hello')
        time.sleep(2)


asyncio
=======

``asyncio`` was introduced with Python 3.4. Experimental support for pySerial
is provided via a separate distribution `pyserial-asyncio`_.

It is currently under development, see:

- http://pyserial-asyncio.readthedocs.io/
- https://github.com/pyserial/pyserial-asyncio

.. _`pyserial-asyncio`: https://pypi.python.org/pypi/pyserial-asyncio

