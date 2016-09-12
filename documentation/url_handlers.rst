.. _URLs:

==============
 URL Handlers
==============

.. module:: serial

Overview
========
The function :func:`serial_for_url` accepts the following types of URLs:

- ``rfc2217://<host>:<port>[?<option>[&<option>...]]``
- ``socket://<host>:<port>[?logging={debug|info|warning|error}]``
- ``loop://[?logging={debug|info|warning|error}]``
- ``hwgrep://<regexp>[&skip_busy][&n=N]``
- ``spy://port[?option[=value][&option[=value]]]``
- ``alt://port?class=<classname>``

.. versionchanged:: 3.0 Options are specified with ``?`` and ``&`` instead of ``/``

Device names are also supported, e.g.:

- ``/dev/ttyUSB0`` (Linux)
- ``COM3`` (Windows)

Future releases of pySerial might add more types. Since pySerial 2.6 it is also
possible for the user to add protocol handlers using
:attr:`protocol_handler_packages`.


``rfc2217://``
==============
Used to connect to :rfc:`2217` compatible servers. All serial port
functions are supported. Implemented by :class:`rfc2217.Serial`.

Supported options in the URL are:

- ``ign_set_control`` does not wait for acknowledges to SET_CONTROL. This
  option can be used for non compliant servers (i.e. when getting an
  ``remote rejected value for option 'control'`` error when connecting).

- ``poll_modem``: The client issues NOTIFY_MODEMSTATE requests when status
  lines are read (CTS/DTR/RI/CD). Without this option it relies on the server
  sending the notifications automatically (that's what the RFC suggests and
  most servers do). Enable this option when :attr:`cts` does not work as
  expected, i.e. for servers that do not send notifications.

- ``timeout=<value>``: Change network timeout (default 3 seconds). This is
  useful when the server takes a little more time to send its answers. The
  timeout applies to the initial Telnet / :rfc:`2271` negotiation as well
  as changing port settings or control line change commands.

- ``logging={debug|info|warning|error}``: Prints diagnostic messages (not
  useful for end users). It uses the logging module and a logger called
  ``pySerial.rfc2217`` so that the application can setup up logging
  handlers etc. It will call :meth:`logging.basicConfig` which initializes
  for output on ``sys.stderr`` (if no logging was set up already).

.. warning:: The connection is not encrypted and no authentication is
             supported! Only use it in trusted environments.


``socket://``
=============
The purpose of this connection type is that applications using pySerial can
connect to TCP/IP to serial port converters that do not support :rfc:`2217`.

Uses a TCP/IP socket. All serial port settings, control and status lines
are ignored. Only data is transmitted and received.

Supported options in the URL are:

- ``logging={debug|info|warning|error}``: Prints diagnostic messages (not
  useful for end users). It uses the logging module and a logger called
  ``pySerial.socket`` so that the application can setup up logging handlers
  etc. It will call :meth:`logging.basicConfig` which initializes for
  output on ``sys.stderr`` (if no logging was set up already).

.. warning:: The connection is not encrypted and no authentication is
             supported! Only use it in trusted environments.


``loop://``
===========
The least useful type. It simulates a loop back connection
(``RX<->TX``  ``RTS<->CTS``  ``DTR<->DSR``). It could be used to test
applications or run the unit tests.

Supported options in the URL are:

- ``logging={debug|info|warning|error}``: Prints diagnostic messages (not
  useful for end users). It uses the logging module and a logger called
  ``pySerial.loop`` so that the application can setup up logging handlers
  etc. It will call :meth:`logging.basicConfig` which initializes for
  output on ``sys.stderr`` (if no logging was set up already).


``hwgrep://``
=============
This type uses :mod:`serial.tools.list_ports` to obtain a list of ports and
searches the list for matches by a regexp that follows the slashes (see Pythons
:py:mod:`re` module for detailed syntax information).

Note that options are separated using the character ``&``, this also applies to
the first, where URLs usually use ``?``. This exception is made as the question
mark is used in regexp itself.

Depending on the capabilities of the ``list_ports`` module on the system, it is
possible to search for the description or hardware ID of a device, e.g. USB
VID:PID or texts.

Unfortunately, on some systems ``list_ports`` only lists a subset of the port
names with no additional information. Currently, on Windows and Linux and
OSX it should find additional information.

Supported options in the URL are:

- ``n=N``: pick the N'th entry instead of the first
- ``skip_busy``: skip ports that can not be opened, e.g. because they are
  already in use. This may not work as expected on platforms where the file is
  not locked automatically (e.g. Posix).


``spy://``
==========
Wrapping the native serial port, this protocol makes it possible to
intercept the data received and transmitted as well as the access to the
control lines, break and flush commands. It is mainly used to debug
applications.

Supported options in the URL are:

- ``file=FILENAME`` output to given file or device instead of stderr
- ``color`` enable ANSI escape sequences to colorize output
- ``raw`` output the read and written data directly (default is to create a
  hex dump). In this mode, no control line and other commands are logged.
- ``all`` also show ``in_waiting`` and empty ``read()`` calls (hidden by
  default because of high traffic).

Example::

    import serial

    with serial.serial_for_url('spy:///dev/ttyUSB0?file=test.txt', timeout=1) as s:
        s.dtr = False
        s.write('hello world')
        s.read(20)
        s.dtr = True
        s.write(serial.to_bytes(range(256)))
        s.read(400)
        s.send_break()

    with open('test.txt') as f:
        print(f.read())

Outputs::

    000000.002 Q-RX reset_input_buffer
    000000.002 DTR  inactive
    000000.002 TX   0000  68 65 6C 6C 6F 20 77 6F  72 6C 64                 hello world     
    000001.015 RX   0000  68 65 6C 6C 6F 20 77 6F  72 6C 64                 hello world     
    000001.015 DTR  active
    000001.015 TX   0000  00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F  ................
    000001.015 TX   0010  10 11 12 13 14 15 16 17  18 19 1A 1B 1C 1D 1E 1F  ................
    000001.015 TX   0020  20 21 22 23 24 25 26 27  28 29 2A 2B 2C 2D 2E 2F   !"#$%&'()*+,-./
    000001.015 TX   0030  30 31 32 33 34 35 36 37  38 39 3A 3B 3C 3D 3E 3F  0123456789:;<=>?
    000001.015 TX   0040  40 41 42 43 44 45 46 47  48 49 4A 4B 4C 4D 4E 4F  @ABCDEFGHIJKLMNO
    000001.016 TX   0050  50 51 52 53 54 55 56 57  58 59 5A 5B 5C 5D 5E 5F  PQRSTUVWXYZ[\]^_
    000001.016 TX   0060  60 61 62 63 64 65 66 67  68 69 6A 6B 6C 6D 6E 6F  `abcdefghijklmno
    000001.016 TX   0070  70 71 72 73 74 75 76 77  78 79 7A 7B 7C 7D 7E 7F  pqrstuvwxyz{|}~.
    000001.016 TX   0080  80 81 82 83 84 85 86 87  88 89 8A 8B 8C 8D 8E 8F  ................
    000001.016 TX   0090  90 91 92 93 94 95 96 97  98 99 9A 9B 9C 9D 9E 9F  ................
    000001.016 TX   00A0  A0 A1 A2 A3 A4 A5 A6 A7  A8 A9 AA AB AC AD AE AF  ................
    000001.016 TX   00B0  B0 B1 B2 B3 B4 B5 B6 B7  B8 B9 BA BB BC BD BE BF  ................
    000001.016 TX   00C0  C0 C1 C2 C3 C4 C5 C6 C7  C8 C9 CA CB CC CD CE CF  ................
    000001.016 TX   00D0  D0 D1 D2 D3 D4 D5 D6 D7  D8 D9 DA DB DC DD DE DF  ................
    000001.016 TX   00E0  E0 E1 E2 E3 E4 E5 E6 E7  E8 E9 EA EB EC ED EE EF  ................
    000001.016 TX   00F0  F0 F1 F2 F3 F4 F5 F6 F7  F8 F9 FA FB FC FD FE FF  ................
    000002.284 RX   0000  00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F  ................
    000002.284 RX   0010  10 11 12 13 14 15 16 17  18 19 1A 1B 1C 1D 1E 1F  ................
    000002.284 RX   0020  20 21 22 23 24 25 26 27  28 29 2A 2B 2C 2D 2E 2F   !"#$%&'()*+,-./
    000002.284 RX   0030  30 31 32 33 34 35 36 37  38 39 3A 3B 3C 3D 3E 3F  0123456789:;<=>?
    000002.284 RX   0040  40 41 42 43 44 45 46 47  48 49 4A 4B 4C 4D 4E 4F  @ABCDEFGHIJKLMNO
    000002.284 RX   0050  50 51 52 53 54 55 56 57  58 59 5A 5B 5C 5D 5E 5F  PQRSTUVWXYZ[\]^_
    000002.284 RX   0060  60 61 62 63 64 65 66 67  68 69 6A 6B 6C 6D 6E 6F  `abcdefghijklmno
    000002.284 RX   0070  70 71 72 73 74 75 76 77  78 79 7A 7B 7C 7D 7E 7F  pqrstuvwxyz{|}~.
    000002.284 RX   0080  80 81 82 83 84 85 86 87  88 89 8A 8B 8C 8D 8E 8F  ................
    000002.284 RX   0090  90 91 92 93 94 95 96 97  98 99 9A 9B 9C 9D 9E 9F  ................
    000002.284 RX   00A0  A0 A1 A2 A3 A4 A5 A6 A7  A8 A9 AA AB AC AD AE AF  ................
    000002.284 RX   00B0  B0 B1 B2 B3 B4 B5 B6 B7  B8 B9 BA BB BC BD BE BF  ................
    000002.284 RX   00C0  C0 C1 C2 C3 C4 C5 C6 C7  C8 C9 CA CB CC CD CE CF  ................
    000002.284 RX   00D0  D0 D1 D2 D3 D4 D5 D6 D7  D8 D9 DA DB DC DD DE DF  ................
    000002.284 RX   00E0  E0 E1 E2 E3 E4 E5 E6 E7  E8 E9 EA EB EC ED EE EF  ................
    000002.284 RX   00F0  F0 F1 F2 F3 F4 F5 F6 F7  F8 F9 FA FB FC FD FE FF  ................
    000002.284 BRK  send_break 0.25

.. versionadded:: 3.0


``alt://``
==========
This handler allows to select alternate implementations of the native serial port.

Currently only the Posix platform provides alternative implementations.

``PosixPollSerial``
    Poll based read implementation. Not all systems support poll properly.
    However this one has better handling of errors, such as a device
    disconnecting while it's in use (e.g. USB-serial unplugged).

``VTIMESerial``
    Implement timeout using ``VTIME``/``VMIN`` of tty device instead of using
    ``select``.  This means that inter character timeout and overall timeout
    can not be used at the same time. Overall timeout is disabled when
    inter-character timeout is used.  The error handling is degraded.

 
Examples::

    alt:///dev/ttyUSB0?class=PosixPollSerial
    alt:///dev/ttyUSB0?class=VTIMESerial

.. versionadded:: 3.0


Examples
========

- ``rfc2217://localhost:7000``
- ``rfc2217://localhost:7000?poll_modem``
- ``rfc2217://localhost:7000?ign_set_control&timeout=5.5``
- ``socket://localhost:7777``
- ``loop://?logging=debug``
- ``hwgrep://0451:f432`` (USB VID:PID)
- ``spy://COM54?file=log.txt``
- ``alt:///dev/ttyUSB0?class=PosixPollSerial``


