.. _examples:

==========
 Examples
==========

.. _miniterm:

Miniterm
========
This is a console application that provides a small terminal application.
Miniterm itself does not implement any terminal features such as VT102
compatibility. However it inherits these features from the terminal it is run.
For example on GNU/Linux running from an xterm it will support the escape
sequences of the xterm. On Windows the typical console window is dumb and does
not support any escapes. When ANSI.sys is loaded it supports some escapes.

Miniterm::

    --- Miniterm on /dev/ttyS0: 9600,8,N,1 ---
    --- Quit: Ctrl+]  |  Menu: Ctrl+T | Help: Ctrl+T followed by Ctrl+H ---

Command line options can be given so that binary data including escapes for
terminals are escaped or output as hex.

Miniterm supports :rfc:`2217` remote serial ports and raw sockets using :ref:`URLs`
such as ``rfc2217:://<host>:<port>`` respectively ``socket://<host>:<port>`` as
*port* argument when invoking.

Command line options ``python -m serial.tools.miniterm -h``::

    Usage: miniterm.py [options] [port [baudrate]]

    Miniterm - A simple terminal program for the serial port.

    Options:
      -h, --help            show this help message and exit

      Port settings:
        -p PORT, --port=PORT
                            port, a number or a device name. (deprecated option,
                            use parameter instead)
        -b BAUDRATE, --baud=BAUDRATE
                            set baud rate, default 9600
        --parity=PARITY     set parity, one of [N, E, O, S, M], default=N
        --rtscts            enable RTS/CTS flow control (default off)
        --xonxoff           enable software flow control (default off)
        --rts=RTS_STATE     set initial RTS line state (possible values: 0, 1)
        --dtr=DTR_STATE     set initial DTR line state (possible values: 0, 1)

      Data handling:
        -e, --echo          enable local echo (default off)
        --cr                do not send CR+LF, send CR only
        --lf                do not send CR+LF, send LF only
        -D, --debug         debug received data (escape non-printable chars)
                            --debug can be given multiple times: 0: just print
                            what is received 1: escape non-printable characters,
                            do newlines as unusual 2: escape non-printable
                            characters, newlines too 3: hex dump everything

      Hotkeys:
        --exit-char=EXIT_CHAR
                            ASCII code of special character that is used to exit
                            the application
        --menu-char=MENU_CHAR
                            ASCII code of special character that is used to
                            control miniterm (menu)

      Diagnostics:
        -q, --quiet         suppress non-error messages


Miniterm supports some control functions. Typing :kbd:`Ctrl+T Ctrl+H` when it is
running shows the help text::

    --- pySerial - miniterm - help
    ---
    --- Ctrl+]   Exit program
    --- Ctrl+T   Menu escape key, followed by:
    --- Menu keys:
    ---       Ctrl+T  Send the menu character itself to remote
    ---       Ctrl+]  Send the exit character to remote
    ---       Ctrl+I  Show info
    ---       Ctrl+U  Upload file (prompt will be shown)
    --- Toggles:
    ---       Ctrl+R  RTS          Ctrl+E  local echo
    ---       Ctrl+D  DTR          Ctrl+B  BREAK
    ---       Ctrl+L  line feed    Ctrl+A  Cycle repr mode
    ---
    --- Port settings (Ctrl+T followed by the following):
    --- p             change port
    --- 7 8           set data bits
    --- n e o s m     change parity (None, Even, Odd, Space, Mark)
    --- 1 2 3         set stop bits (1, 2, 1.5)
    --- b             change baud rate
    --- x X           disable/enable software flow control
    --- r R           disable/enable hardware flow control

.. versionchanged:: 2.5
    Added :kbd:`Ctrl+T` menu and added support for opening URLs.
.. versionchanged:: 2.6
    File moved from the examples to :mod:`serial.tools.miniterm`.

miniterm.py_
    The miniterm program.

setup-miniterm-py2exe.py_
    This is a py2exe setup script for Windows. It can be used to create a
    standalone ``miniterm.exe``.

.. _miniterm.py: http://sourceforge.net/p/pyserial/code/HEAD/tree/trunk/pyserial/serial/tools/miniterm.py
.. _setup-miniterm-py2exe.py: http://sourceforge.net/p/pyserial/code/HEAD/tree/trunk/pyserial/examples/setup-miniterm-py2exe.py


TCP/IP - serial bridge
======================
This program opens a TCP/IP port. When a connection is made to that port (e.g.
with telnet) it forwards all data to the serial port and vice versa.

This example only exports a raw socket connection. The next example
below gives the client much more control over the remote serial port.

- The serial port settings are set on the command line when starting the
  program.
- There is no possibility to change settings from remote.
- All data is passed through as-is.

::

    Usage: tcp_serial_redirect.py [options] [port [baudrate]]

    Simple Serial to Network (TCP/IP) redirector.

    Options:
      -h, --help            show this help message and exit
      -q, --quiet           suppress non error messages
      --spy                 peek at the communication and print all data to the
                            console

      Serial Port:
        Serial port settings

        -p PORT, --port=PORT
                            port, a number (default 0) or a device name
        -b BAUDRATE, --baud=BAUDRATE
                            set baud rate, default: 9600
        --parity=PARITY     set parity, one of [N, E, O], default=N
        --rtscts            enable RTS/CTS flow control (default off)
        --xonxoff           enable software flow control (default off)
        --rts=RTS_STATE     set initial RTS line state (possible values: 0, 1)
        --dtr=DTR_STATE     set initial DTR line state (possible values: 0, 1)

      Network settings:
        Network configuration.

        -P LOCAL_PORT, --localport=LOCAL_PORT
                            local TCP port
        --rfc2217           allow control commands with Telnet extension RFC-2217

      Newline Settings:
        Convert newlines between network and serial port. Conversion is
        normally disabled and can be enabled by --convert.

        -c, --convert       enable newline conversion (default off)
        --net-nl=NET_NEWLINE
                            type of newlines that are expected on the network
                            (default: LF)
        --ser-nl=SER_NEWLINE
                            type of newlines that are expected on the serial port
                            (default: CR+LF)

    NOTE: no security measures are implemented. Anyone can remotely connect to
    this service over the network.  Only one connection at once is supported. When
    the connection is terminated it waits for the next connect.


tcp_serial_redirect.py_
    Main program.

.. _tcp_serial_redirect.py: http://sourceforge.net/p/pyserial/code/HEAD/tree/trunk/pyserial/examples/tcp_serial_redirect.py


Single-port TCP/IP - serial bridge (RFC 2217)
=============================================
Simple cross platform :rfc:`2217` serial port server. It uses threads and is
portable (runs on POSIX, Windows, etc).

- The port settings and control lines (RTS/DTR) can be changed at any time
  using :rfc:`2217` requests. The status lines (DSR/CTS/RI/CD) are polled every
  second and notifications are sent to the client.
- Telnet character IAC (0xff) needs to be doubled in data stream. IAC followed
  by an other value is interpreted as Telnet command sequence.
- Telnet negotiation commands are sent when connecting to the server.
- RTS/DTR are activated on client connect and deactivated on disconnect.
- Default port settings are set again when client disconnects.

::

    Usage: rfc2217_server.py [options] port

    RFC 2217 Serial to Network (TCP/IP) redirector.

    Options:
      -h, --help            show this help message and exit
      -p LOCAL_PORT, --localport=LOCAL_PORT
                            local TCP port

    NOTE: no security measures are implemented. Anyone can remotely connect to
    this service over the network.  Only one connection at once is supported. When
    the connection is terminated it waits for the next connect.

.. versionadded:: 2.5

rfc2217_server.py_
    Main program.

setup-rfc2217_server-py2exe.py_
    This is a py2exe setup script for Windows. It can be used to create a
    standalone ``rfc2217_server.exe``.

.. _rfc2217_server.py: http://sourceforge.net/p/pyserial/code/HEAD/tree/trunk/pyserial/examples/rfc2217_server.py
.. _setup-rfc2217_server-py2exe.py: http://sourceforge.net/p/pyserial/code/HEAD/tree/trunk/pyserial/examples/setup-rfc2217_server-py2exe.py


Multi-port TCP/IP - serial bridge (RFC 2217)
============================================
This example implements a TCP/IP to serial port service that works with
multiple ports at once. It uses select, no threads, for the serial ports and
the network sockets and therefore runs on POSIX systems only.

- Full control over the serial port with :rfc:`2217`.
- Check existence of ``/tty/USB0...8``. This is done every 5 seconds using
  ``os.path.exists``.
- Send zeroconf announcements when port appears or disappears (uses
  python-avahi and dbus). Service name: ``_serial_port._tcp``.
- Each serial port becomes available as one TCP/IP server. e.g.
  ``/dev/ttyUSB0`` is reachable at ``<host>:7000``.
- Single process for all ports and sockets (not per port).
- The script can be started as daemon.
- Logging to stdout or when run as daemon to syslog.
- Default port settings are set again when client disconnects.
- modem status lines (CTS/DSR/RI/CD) are not polled periodically and the server
  therefore does not send NOTIFY_MODEMSTATE on its own. However it responds to
  request from the client (i.e. use the ``poll_modem`` option in the URL when
  using a pySerial client.)

Requirements:

- Python (>= 2.4)
- python-avahi
- python-dbus
- python-serial (>= 2.5)

Installation as daemon:

- Copy the script ``port_publisher.py`` to ``/usr/local/bin``.
- Copy the script ``port_publisher.sh`` to ``/etc/init.d``.
- Add links to the runlevels using ``update-rc.d port_publisher.sh defaults 99``
- Thats it :-) the service will be started on next reboot. Alternatively run
  ``invoke-rc.d port_publisher.sh start`` as root.

.. versionadded:: 2.5 new example

port_publisher.py_
    Multi-port TCP/IP-serial converter (RFC 2217) for POSIX environments.

port_publisher.sh_
    Example init.d script.

.. _port_publisher.py: http://sourceforge.net/p/pyserial/code/HEAD/tree/trunk/pyserial/examples/port_publisher.py
.. _port_publisher.sh: http://sourceforge.net/p/pyserial/code/HEAD/tree/trunk/pyserial/examples/port_publisher.sh


wxPython examples
=================
A simple terminal application for wxPython and a flexible serial port
configuration dialog are shown here.

wxTerminal.py_
    A simple terminal application. Note that the length of the buffer is
    limited by wx and it may suddenly stop displaying new input.

wxTerminal.wxg_
    A wxGlade design file for the terminal application.

wxSerialConfigDialog.py_
    A flexible serial port configuration dialog.

wxSerialConfigDialog.wxg_
    The wxGlade design file for the configuration dialog.

setup-wxTerminal-py2exe.py_
    A py2exe setup script to package the terminal application.

.. _wxTerminal.py: http://sourceforge.net/p/pyserial/code/HEAD/tree/trunk/pyserial/examples/wxTerminal.py
.. _wxTerminal.wxg: http://sourceforge.net/p/pyserial/code/HEAD/tree/trunk/pyserial/examples/wxTerminal.wxg
.. _wxSerialConfigDialog.py: http://sourceforge.net/p/pyserial/code/HEAD/tree/trunk/pyserial/examples/wxSerialConfigDialog.py
.. _wxSerialConfigDialog.wxg: http://sourceforge.net/p/pyserial/code/HEAD/tree/trunk/pyserial/examples/wxSerialConfigDialog.wxg
.. _setup-wxTerminal-py2exe.py: http://sourceforge.net/p/pyserial/code/HEAD/tree/trunk/pyserial/examples/setup-wxTerminal-py2exe.py


Wrapper class
=============
This example provides a subclass based on ``Serial`` that has an alternative
implementation of ``readline()``

enhancedserial.py_
    A class with alternative ``readline()`` implementation.

.. _enhancedserial.py: http://sourceforge.net/p/pyserial/code/HEAD/tree/trunk/pyserial/examples/enhancedserial.py


Unit tests
==========
The project uses a number of unit test to verify the functionality. They all
need a loop back connector. The scripts itself contain more information. All
test scripts are contained in the directory ``test``.

The unit tests are performed on port ``0`` unless a different device name or
``rfc2217://`` URL is given on the command line (argv[1]).

run_all_tests.py_
    Collect all tests from all ``test*`` files and run them. By default, the
    ``loop://`` device is used.

test.py_
    Basic tests (binary capabilities, timeout, control lines).

test_advanced.py_
    Test more advanced features (properties).

test_high_load.py_
    Tests involving sending a lot of data.

test_readline.py_
    Tests involving readline.

test_iolib.py_
    Tests involving the :mod:`io` library. Only available for Python 2.6 and
    newer.

test_url.py_
    Tests involving the :ref:`URL <URLs>` feature.

.. _run_all_tests.py:  http://sourceforge.net/p/pyserial/code/HEAD/tree/trunk/pyserial/test/run_all_tests.py
.. _test.py:           http://sourceforge.net/p/pyserial/code/HEAD/tree/trunk/pyserial/test/test.py
.. _test_advanced.py:  http://sourceforge.net/p/pyserial/code/HEAD/tree/trunk/pyserial/test/test_advanced.py
.. _test_high_load.py: http://sourceforge.net/p/pyserial/code/HEAD/tree/trunk/pyserial/test/test_high_load.py
.. _test_readline.py:  http://sourceforge.net/p/pyserial/code/HEAD/tree/trunk/pyserial/test/test_readline.py
.. _test_iolib.py:     http://sourceforge.net/p/pyserial/code/HEAD/tree/trunk/pyserial/test/test_iolib.py
.. _test_url.py:       http://sourceforge.net/p/pyserial/code/HEAD/tree/trunk/pyserial/test/test_url.py
