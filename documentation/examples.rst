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

Command line options can be given so that binary data including escapes for
terminals are escaped or output as hex.

miniterm supports some control functions. Typing ``CTRL+T CTRL+H`` when it is
running shows the help text.

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

scanwin32.py_
    A Windows only version that returns a list of serial ports with information
    from the registry.

.. _scan.py: http://pyserial.svn.sourceforge.net/viewvc/*checkout*/pyserial/trunk/pyserial/examples/scan.py
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
