==========
 Examples
==========

Miniterm
========
This is a console application that provides a small terminal application.
miniterm itself does not implement any terminal features such as VT102
compatibility. However it inherits these features from the terminal it is run.
For example on GNU/Linux running from an xterm it will support the escape
sequences of the xterm. On Windows the typical console window is dumb and does
not support any escapes. When ANSI.sys is loaded it supports some escapes.

miniterm::

    --- Miniterm on /dev/ttyS0: 9600,8,N,1 ---
    --- Quit: Ctrl+]  |  Menu: Ctrl+T | Help: Ctrl+T followed by Ctrl+H ---

Command line options can be given so that binary data including escapes for
terminals are escaped or output as hex.

Command line options ``miniterm.py -h``::

    Usage: miniterm.py [options] [port [baudrate]]

    Miniterm - A simple terminal program for the serial port.

    Options:
      -h, --help            show this help message and exit
      -p PORT, --port=PORT  port, a number (default 0) or a device name
                            (deprecated option)
      -b BAUDRATE, --baud=BAUDRATE
                            set baud rate, default 9600
      --parity=PARITY       set parity, one of [N, E, O, S, M], default=N
      -e, --echo            enable local echo (default off)
      --rtscts              enable RTS/CTS flow control (default off)
      --xonxoff             enable software flow control (default off)
      --cr                  do not send CR+LF, send CR only
      --lf                  do not send CR+LF, send LF only
      -D, --debug           debug received data (escape non-printable chars)
                            --debug can be given multiple times: 0: just print
                            what is received 1: escape non-printable characters,
                            do newlines as unusual 2: escape non-printable
                            characters, newlines too 3: hex dump everything
      --rts=RTS_STATE       set initial RTS line state (possible values: 0, 1)
      --dtr=DTR_STATE       set initial DTR line state (possible values: 0, 1)
      -q, --quiet           suppress non error messages
      --exit-char=EXIT_CHAR
                            ASCII code of special character that is used to exit
                            the application
      --menu-char=MENU_CHAR
                            ASCII code of special character that is used to
                            control miniterm (menu)


miniterm supports some control functions. Typing :kbd:`Control+t Control+h` when it is
running shows the help text::

    --- pySerial - miniterm - help
    ---
    --- Ctrl+]   Exit program
    --- Ctrl+T   Menu escape key, followed by:
    --- Menu keys:
    ---       Ctrl+T   Send the menu character itself to remote
    ---       Ctrl+]   Send the exit character to remote
    ---       Ctrl+I   Show info
    ---       Ctrl+U   Upload file (prompt will be shown)
    --- Toggles:
    ---       Ctrl+R  RTS          Ctrl+E  local echo
    ---       Ctrl+D  DTR          Ctrl+B  BREAK
    ---       Ctrl+L  line feed    Ctrl+A  Cycle repr mode
    ---
    --- Port settings (Ctrl+T followed by the following):
    --- 7 8           set data bits
    --- n e o s m     change parity (None, Even, Odd, Space, Mark)
    --- 1 2 3         set stop bits (1, 2, 1.5)
    --- b             change baud rate
    --- x X           disable/enable software flow control
    --- r R           disable/enable hardware flow control


miniterm.py_
    The miniterm program.

setup-miniterm-py2exe.py_
    This is a py2exe setup script for Windows. It can be used to create a
    standalone ``miniterm.exe``.

.. _miniterm.py: http://pyserial.svn.sourceforge.net/viewvc/*checkout*/pyserial/trunk/pyserial/examples/miniterm.py
.. _setup-miniterm-py2exe.py: http://pyserial.svn.sourceforge.net/viewvc/*checkout*/pyserial/trunk/pyserial/examples/setup-miniterm-py2exe.py


TCP/IP - serial bridge
======================
This program opens a TCP/IP port. When a connection is made to that port (e.g.
with telnet) it forwards all data to the serial port and vice versa.

The serial port settings are set on the command line when starting the program.
There is no possibility to change settings from remote.
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

.. _tcp_serial_redirect.py: http://pyserial.svn.sourceforge.net/viewvc/*checkout*/pyserial/trunk/pyserial/examples/tcp_serial_redirect.py


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

setup_demo.py_
    A py2exe setup script to package the terminal application.

.. _wxTerminal.py: http://pyserial.svn.sourceforge.net/viewvc/*checkout*/pyserial/trunk/pyserial/examples/wxTerminal.py
.. _wxTerminal.wxg: http://pyserial.svn.sourceforge.net/viewvc/*checkout*/pyserial/trunk/pyserial/examples/wxTerminal.wxg
.. _wxSerialConfigDialog.py: http://pyserial.svn.sourceforge.net/viewvc/*checkout*/pyserial/trunk/pyserial/examples/wxSerialConfigDialog.py
.. _wxSerialConfigDialog.wxg: http://pyserial.svn.sourceforge.net/viewvc/*checkout*/pyserial/trunk/pyserial/examples/wxSerialConfigDialog.wxg
.. _setup_demo.py: http://pyserial.svn.sourceforge.net/viewvc/*checkout*/pyserial/trunk/pyserial/examples/setup_demo.py


Wrapper class
=============
This example provides a subclass based on ``Serial`` that has an alternative
implementation of ``readline()``

enhancedserial.py_
    A class with alternative ``readline()`` implementation.

.. _enhancedserial.py: http://pyserial.svn.sourceforge.net/viewvc/*checkout*/pyserial/trunk/pyserial/examples/enhancedserial.py


Finding serial ports
====================
scan.py_
    A simple loop that probes serial ports by number.

scanlinux.py_
    A Linux only version looking at the entries in ``/dev``. It works best with
    on systems with devfs or udev that only create those entries that represent
    devices. On older installations a lot of pre-created device files are found
    and an additional open check should be added to ensure that the device is
    real.

scanwin32.py_
    A Windows only version that returns a list of serial ports with information
    from the registry.

.. _scan.py: http://pyserial.svn.sourceforge.net/viewvc/*checkout*/pyserial/trunk/pyserial/examples/scan.py
.. _scanlinux.py: http://pyserial.svn.sourceforge.net/viewvc/*checkout*/pyserial/trunk/pyserial/examples/scanlinux.py
.. _scanwin32.py: http://pyserial.svn.sourceforge.net/viewvc/*checkout*/pyserial/trunk/pyserial/examples/scanwin32.py


Unit tests
==========
The project uses a number of unit test to verify the functionality. They all
need a loop back connector. The scripts itself contain more information.

test.py_
    Basic tests.

test_high_load.py_
    Tests involving sending a lot of data.

test_advanced.py_
    Test more advanced features.

.. _test.py: http://pyserial.svn.sourceforge.net/viewvc/*checkout*/pyserial/trunk/pyserial/examples/test.py
.. _test_high_load.py: http://pyserial.svn.sourceforge.net/viewvc/*checkout*/pyserial/trunk/pyserial/examples/test_high_load.py
.. _test_advanced.py: http://pyserial.svn.sourceforge.net/viewvc/*checkout*/pyserial/trunk/pyserial/examples/test_advanced.py
