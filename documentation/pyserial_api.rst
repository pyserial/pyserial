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
