========================
 pySerial Release Notes
========================

Version 1.0     13 Feb 2002
---------------------------
- First public release.
- Split from the pybsl application (see http://mspgcc.sourceforge.net)

New Features:

- Added Jython support


Version 1.1     14 Feb 2002
---------------------------
Bugfixes:

- Win32, when not specifying a timeout
- Typos in the Docs

New Features:

- added ``serialutil`` which provides a base class for the ``Serial``
  objects.

- ``readline``, ``readlines``, ``writelines`` and ``flush`` are now supported
  see README.txt for deatils.


Version 1.11    14 Feb 2002
---------------------------
Same as 1.1 but added missing files.


Version 1.12    18 Feb 2002
---------------------------
Removed unneded constants to fix RH7.x problems.


Version 1.13    09 Apr 2002
---------------------------
Added alternate way for enabling rtscts (CNEW_RTSCTS is tried too)
If port opening fails, a ``SerialException`` is raised on all platforms


Version 1.14    29 May 2002
---------------------------
Added examples to archive
Added non-blocking mode for ``timeout=0`` (tnx Mat Martineau)

Bugfixes:

- win32 does now return the remaining characters on timeout


Version 1.15    04 Jun 2002
---------------------------
Bugfixes (win32):

- removed debug messages
- compatibility to win9x improved


Version 1.16    02 Jul 2002
---------------------------
Added implementation of RI and corrected RTS/CTS on Win32


Version 1.17    03 Jul 2002
---------------------------
Silly mix of two versions in win32 code corrected


Version 1.18    06 Dec 2002
---------------------------
Bugfixes (general):

- remove the mapping of flush to the destructive flushOutput as
  this is not the expected behaviour.
- readline: EOL character for lines can be chosen idea by 
  John Florian.

Bugfixes (posix):

- cygwin port numbering fixed
- test each and every constant for it's existence in termios module,
  use default if not existent (fix for Bug item #640214)
- wrong exception on nonexistent ports with /dev file. bug report
  by Louis Cordier

Bugfixes (win32):

- RTS/CTS handling as suggested in Bug #635072
- bugfix of timeouts brought up by Markus Hoffrogge


Version 1.19    19 Mar 2003
---------------------------
Bugfixes (posix):

- removed ``dgux`` entry which actually had a wrong comment and is
  probably not in use anywhere.

Bugfixes (win32):

- added ``int()`` conversion, [Bug 702120]
- remove code to set control lines in close method of win32
  version. [Bug 669625]


Version 1.20    28 Aug 2003
---------------------------
- Added ``serial.device()`` for all platforms

Bugfixes (win32):

- don't recreate overlapped structures and events on each
  read/write.
- don't set unneeded event masks.
- don't use DOS device names for ports > 9.
- remove send timeout (it's not used in the linux impl. anyway).


Version 1.21    30 Sep 2003
---------------------------
Bugfixes (win32):

- name for COM10 was not built correctly, found by Norm Davis.

Bugfixes (examples):

- small change in ``miniterm.py`` that should mage it run on cygwin,
  [Bug 809904] submitted by Rolf Campbell.


Version 2.0b1    1 Oct 2003
---------------------------
Transition to the Python 2.0 series:

- New implementation only supports Python 2.2+, backwards compatibility
  should be maintained almost everywhere.
  The OS handles (like the ``hComPort`` or ``fd`` attribute) were prefixed
  with an underscore. The different names stay, as anyone that uses one of
  these has to write platform specific code anyway.
- Common base class ``serialutil.SerialBase`` for all implementations.
- ``PARITY_NONE``, ``PARITY_EVEN``, ``PARITY_ODD`` constants changed and all
  these constants moved to ``serialutil.py`` (still available as
  ``serial.PARITY_NONE`` etc. and they should be used that way)
- Added ``serial.PARITY_NAMES`` (implemented in ``serialutil.PARITY_NAMES``).
  This dictionary can be used to convert parity constants to meaningful
  strings.
- Each Serial class and instance has a list of supported values:
  ``BAUDRATES``, ``BYTESIZES``, ``PARITIES``, ``STOPBITS``Ggg
  (i.e. ``serial.Serial.BAUDRATES or s = serial.Serial; s.BAUDRATES``)
  these values can be used to fill in value sin GUI dialogs etc.
- Creating a ``Serial()`` object without port spec returns an unconfigured,
  closed port. Useful if a GUI dialog should take a port and configure
  it.
- New methods for ``serial.Serial`` instances: ``open()``, ``isOpen()``
- A port can be opened and closed as many times as desired.
- Instances of ``serial.Serial`` have ``baudrate``, ``bytesize``, ``timeout``
  etc. attributes implemented as properties, all can be set while the port is
  opened. It will then be reconfigured.
- Improved ``__doc__``'s.
- New ``test_advanced.py`` for the property setting/getting testing.
- Small bugfix on posix with get* methods (return value should be true a
  boolean).
- added a ``__repr__`` that returns a meaningful string will all the serial
  setting, easy for debugging.
- The serialposix module does not throw an exception on unsupported
  platforms, the message is still printed. The idea that it may still
  work even if the platform itself s not known, it simply tries to do
  the posix stuff anyway (It's likely that opening ports by number
  fails, but by name it should work).


Version 2.0b2    4 Oct 2003
---------------------------
- Added serial port configuration dialog for wxPython to the examples.
- Added terminal application for wxPython with wxGlade design file
  to the examples.
- Jython support is currently broken as Jython does not have a Python 2.2
  compatible release out yet


Version 2.0      6 Nov 2003
---------------------------
- Fixes ``setup.py`` for older distutils


Version 2.1     28 Jul 2004
---------------------------
Bugfixes:

- Fix XON/XOFF values [Bug 975250]

Bugfixes (posix):

- ``fd == 0`` fix from Vsevolod Lobko
- netbsd fixes from Erik Lindgren
- Dynamically lookup baudrates and some cleanups

Bugfixes (examples):

- CRLF handling of ``miniterm.py`` should be more consistent on Win32
  and others. Added LF only command line option
- Multithreading fixes to ``wxTerminal.py`` (helps with wxGTK)
- Small change for wxPython 2.5 in ``wxSerialConfigDialog.py`` [Bug 994856]

New Features:

- Implement write timeouts (``writeTimeout`` parameter)


Version 2.2     31 Jul 2005
---------------------------
Bugfixes:

- [Bug 1014227]: property <del> broken
- [Bug 1105687]: ``serial_tcp_example.py``: ``--localport`` option
- [Bug 1106313]: device (port) strings cannot be unicode

Bugfixes (posix):

- [Patch 1043436] Fix for [Bug 1043420] (OSError: EAGAIN)
- [Patch 1102700] ``fileno()`` added
- ensure disabled PARMRK

Bugfixes (win32):

- [Patch 983106]: keep RTS/CTS state on port setting changes

New Features:

- ``dsrdtr`` setting to enable/disable DSR/DTR flow control independently
  from the ``rtscts`` setting. (Currently Win32 only, ignored on other
  platforms)


Version 2.3     19 Jun 2008
---------------------------
New Features:

- iterator interface. ``for line in Serial(...): ...`` is now possible
  Suggested by Bernhard Bender
- ``sendBreak()`` accepts a ``duration`` argument. Default duration increased.
- win32 handles \\.\COMx format automatically for com ports of higher number
  (COM10 is internally translated to \\.\COM10 etc.)
- miniterm.py has a new feature to send a file (upload) and configurable
  special characters for exit and upload. Refactored internals to class based
  structure (upload and class refactoring by Colin D Bennett)

Bugfixes:

- [Bug 1451535] TCP/serial redirect example "--help"
- update VERSION variable
- update wxSerialConfigDialog.py and wxTerminal.py compatibility with
  wxPython 2.8 (Peleg)
- Check for string in write function. Using unicode causes errors, this
  helps catching errors early (Tom Lynn)

Bugfixes (posix):

- [Bug 1554183] setRTS/setDTR reference to non existing local "on"
- [Bug 1513653] file descriptor not closed when exception is thrown
- FreeBSD now uses cuadX instead of cuaaX (Patrick Phalen)

Bugfixes (win32):

- [Bug 1520357] Handle leak
- [Bug 1679013] Ignore exception raised by SetCommTimeout() in close().
- [Bug 1938118] process hang forever under XP


Version 2.4      6 Jul 2008
---------------------------
New Features:

- [Patch 1616790] pyserial: Add inter-character timeout feature
- [Patch 1924805] add a setBreak function
- Add mark/space parity
- Add .NET/Mono backend (IronPython)

Bugfixes (posix):

- [Bug 1783159] Arbitrary baud rates (Linux/Posix)

Bugfixes (win32):

- [Patch 1561423] Add mark/space parity, Win32
- [Bug 2000771] serial port CANNOT be specified by number on windows
- examples/scanwin32.py does no longer return \\.\ names
- fix \\.\ handling for some cases

Bugfixes (jython):

 - The Jython backend tries javax.comm and gnu.io (Seo Sanghyeon)


Version 2.5-rc1  2009-07-30
---------------------------
New Features:

- Python 3.x support (through 2to3)
- compatible with Python io library (Python 2.6+)
- Support for Win32 is now written on the top of ctypes (bundled with
  Python 2.5+) instead of pywin32 (patch by Giovanni Bajo).
- 1.5 stop bits (STOPBITS_ONE_POINT_FIVE, implemented on all platforms)
- miniterm application extended (CTRL+T -> menu)
- miniterm.py is now installed as "script"
- add scanlinux.py example
- add port_publisher example
- experimental RFC-2217 server support (examples/rfc2217_server.py)
- add ``getSettingsDict`` and ``applySettingsDict`` serial object methods
- use a ``poll`` based implementation on Posix, instead of a ``select`` based,
  provides better error handling [removed again in later releases].

Bugfixes:

- Improve and fix tcp_serial_redirector example.
- [Bug 2603052] 5-bit mode (needs 1.5 stop bits in some cases)

Bugfixes (posix):

- [Bug 2810169] Propagate exceptions raised in serialposix _reconfigure
- [Bug 2562610] setting non standard baud rates on Darwin (Emmanuel Blot)

Bugfixes (win32):

- [Bug 2469098] parity PARITY_MARK, PARITY_SPACE isn't supported on win32
- [SF  2446218] outWaiting implemented
- [Bug 2392892] scanwin32.py better exception handling
- [Bug 2505422] scanwin32.py Vista 64bit compatibility


Version 2.5-rc2  2010-01-02
---------------------------
New Features:

- Documentation update, now written with Sphinx/ReST
- Updated miniterm.py example
- experimental RFC-2217 client support (serial.rfc2217.Serial, see docs)
- add ``loop://`` device for testing.
- add ``serial.serial_for_url`` factory function (support for native ports and
  ``rfc2217``, ``socket`` and ``loop`` URLs)
- add new example: ``rfc2217_server.py``
- tests live in their own directory now (no longer in examples)

Bugfixes:

- [Bug 2915810] Fix for suboption parsing in rfc2217
- Packaging bug (missed some files)

Bugfixes (posix):

- improve write timeout behavior
- [Bug 2836297] move Linux specific constants to not break other platforms
- ``poll`` based implementation for ``read`` is in a separate class
  ``PosixPollSerial``, as it is not supported well on all platforms (the
  default ``Serial`` class uses select).
- changed error handling in ``read`` so that disconnected devices are
  detected.


Bugfixes (win32):

- [Bug 2886763] hComPort doesn't get initialized for Serial(port=None)


Version 2.5      2010-07-22
---------------------------
New Features:

- [Bug 2976262] dsrdtr should default to False
  ``dsrdtr`` parameter default value changed from ``None`` (follow ``rtscts``
  setting) to ``False``. This means ``rtscts=True`` enables hardware flow
  control on RTS/CTS but no longer also on DTR/DSR. This change mostly
  affects Win32 as on other platforms, that setting was ignored anyway.
- Improved xreadlines, it is now a generator function that yields lines as they
  are received (previously it called readlines which would only return all
  lines read after a read-timeout). However xreadlines is deprecated and not
  available when the io module is used. Use ``for line in Serial(...):``
  instead.

Bugfixes:

- [Bug 2925854] test.py produces exception with python 3.1
- [Bug 3029812] 2.5rc2 readline(s) doesn't work

Bugfixes (posix):

- [BUG 3006606] Nonblocking error - Unix platform

Bugfixes (win32):

- [Bug 2998169] Memory corruption at faster transmission speeds.
  (bug introduced in 2.5-rc1)


Version 2.6      2011-11-02
---------------------------
New Features:

- Moved some of the examples to serial.tools so that they can be used
  with ``python -m``
- serial port enumeration now included as ``serial.tools.list_ports``
- URL handlers for ``serial_for_url`` are now imported dynamically. This allows
  to add protocols w/o editing files. The list
  ``serial.protocol_handler_packages`` can be used to add or remove user
  packages with protocol handlers (see docs for details).
- new URL type: hwgrep://<regexp> uses list_ports module to search for ports
  by their description
- several internal changes to improve Python 3.x compatibility (setup.py,
  use of absolute imports and more)

Bugfixes:

- [Bug 3093882] calling open() on an already open port now raises an exception
- [Bug 3245627] connection-lost let rfc2217 hangs in closed loop
- [Patch 3147043] readlines() to support multi-character eol

Bugfixes (posix):

- [Patch 3316943] Avoid unneeded termios.tcsetattr calls in serialposix.py
- [Patch 2912349] Serial Scan as a Module with Mac Support

Bugfixes (win32):

- [Bug 3057499] writeTimeoutError when write Timeout is 0
- [Bug 3414327] Character out of range in list_ports_windows
- [Patch 3036175] Windows 98 Support fix
- [Patch 3054352] RTS automatic toggle, for RS485 functionality.
- Fix type definitions for 64 bit Windows compatibility


Version 2.7      2013-10-17
---------------------------
- Win32: setRTS and setDTR can be called before the port is opened and it will
  set the initial state on port open.
- Posix: add platform specific method: outWaiting (already present for Win32)
- Posix: rename flowControl to setXON to match name on Win32, add
  flowControlOut function
- rfc2217: zero polls value (baudrate, data size, stop bits, parity) (Erik
  Lundh)
- Posix: [Patch pyserial:28] Accept any speed on Linux [update]
- Posix: [Patch pyserial:29] PosixSerial.read() should "ignore" errno.EINTR
- OSX: [Patch pyserial:27] Scan by VendorID/Product ID for USB Serial devices
- Ensure working with bytes in write() calls

Bugfixes:

- [Bug 3540332] SerialException not returned
- [Bug pyserial:145] Error in socket_connection.py
- [Bug pyserial:135] reading from socket with timeout=None causes TypeError
- [Bug pyserial:130] setup.py should not append py3k to package name
- [Bug pyserial:117] no error on lost conn w/socket://

Bugfixes (posix):

- [Patch 3462364] Fix: NameError: global name 'base' is not defined
- list_ports and device() for BSD updated (Anders Langworthy)
- [Bug 3518380] python3.2 -m serial.tools.list_ports error
- [Bug pyserial:137] Patch to add non-standard baudrates to Cygwin
- [Bug pyserial:141] open: Pass errno from IOError to SerialException
- [Bug pyserial:125] Undefined 'base' on list_ports_posix.py, function usb_lsusb
- [Bug pyserial:151] Serial.write() without a timeout uses 100% CPU on POSIX
- [Patch pyserial:30] [PATCH 1/1] serial.Serial() should not raise IOError.

Bugfixes (win32):

- [Bug 3444941] ctypes.WinError() unicode error
- [Bug 3550043] on Windows in tools global name 'GetLastError' is not defined
- [Bug pyserial:146] flush() does nothing in windows (despite docs)
- [Bug pyserial:144] com0com ports ignored due to missing "friendly name"
- [Bug pyserial:152] Cannot configure port, some setting was wrong. Can leave
  port handle open but port not accessible


Version 3.0a0   2015-09-22
--------------------------
- Starting from this release, only Python 2.7 and 3.2 (or newer) are supported.
  The source code is compatible to the 2.x and 3.x series without any changes.
  The support for earlier Python versions than 2.7 is removed, please refer to
  the pyserial-legacy (V2.x) series if older Python versions are a
  requirement).
- Development moved to github, update links in docs.
- API changes: properties for ``rts``, ``dtr``, ``cts``, ``dsr``, ``cd``, ``ri``,
  ``in_waiting`` (instead of get/set functions)
- remove file ``FileLike`` class, add ``read_until`` and ``iread_until`` to
  ``SerialBase``
- RS485 support changed (``rts_toggle`` removed, added ``serial.rs485`` module
  and ``rs485_mode`` property)
- ``socket://`` and ``rfc2217://`` handlers use the IPv6 compatible
  ``socket.create_connection``
- New URL handler: ``spy:://``.
- URL handlers now require the proper format (``?`` and ``&``) for arguments
  instead of ``/`` (e.g. ``rfc2217://localhost:7000?ign_set_control&timeout=5.5``)
- Remove obsolete examples.
- Finish update to BSD license.
- Use setuptools if available, fall back to distutils if unavailable.
- miniterm: changed command line options
- miniterm: support encodings on serial port
- miniterm: new transformations, by default escape/convert all control characters
- list_ports: improved, added USB location (Linux, Win32)
- refactored code
- [FTR pyserial:37] Support fileno() function in the socket protocol
- Posix: [Patch pyserial:31] Mark/space parity on Linux
- Linux: [Patch pyserial:32] Module list_ports for linux should include the
  product information as description.
- Java: fix 2 bugs (stop bits if/else and non-integer timeouts) (Torsten
  Roemer)
- Update wxSerialConfigDialog.py to use serial.tools.list_ports.
- [Patch pyserial:34] Improvements to port_publisher.py example
- [Feature pyserial:39] Support BlueTooth serial port discovery on Linux

Bugfixes:

- [Bug pyserial:157] Implement inWaiting in protocol_socket
- [Bug pyserial:166] RFC2217 connections always fail
- [Bug pyserial:172] applySettingsDict() throws an error if the settings dictionary is not complete
- [Bug pyserial:185] SocketSerial.read() never returns data when timeout==0

Bugfixes (posix):

- [Bug pyserial:156] PosixSerial.open raises OSError rather than
  SerialException when port open fails
- [Bug pyserial:163] serial.tools.list_ports.grep() fails if it encounters None type
- fix setXON
- [Patch pyserial:36 / 38] Make USB information work in python 3.4 and 2.7
- clear OCRNL/ONLCR flags (CR/LF translation settings)
- [Feature pyserial:38] RS485 Support
- [Bug pyserial:170] list_ports_posix not working properly for Cygwin
- [Bug pyserial:187] improve support for FreeBSD (list_ports_posix)

Bugfixes (win32):

- [Bug pyserial:169] missing "import time" in serialwin32.py

Bugfixes (cli):

- [Bug pyserial:159] write() in serialcli.py not working with IronPython 2.7.4


Version 3.0b1   2015-10-19
--------------------------
- list_ports: add ``vid``, ``pid``, ``serial_number``, ``product``,
  ``manufacturer`` and ``location`` attribute for USB devices.
- list_ports: update OSX implementation.
- list_ports: Raspberry Pi: internal port is found.
- serial_for_url: fix import (multiple packages in list)
- threaded: added new module implementing a reader thread
- tweak examples/wx*
- posix: add experimental implementation ``VTIMESerial``
- new URL handler ``alt://`` to select alternative implementations


Version 3.0   2015-12-28
------------------------
- minor fixes to setup.py (file list), inter_byte_timeout (not stored when
  passed to __init__), rfc2217 (behavior of close when open failed),
  list_ports (__str__), loop://, renamed ReaderThread
- hwgrep:// added options to pick n'th port, skip busy ports
- miniterm: --ask option added

Bugfixes (posix):

- [#26/#30] always call tcsettattr on open
- [#42] fix disregard read timeout if there is more data
- [#45] check for write timeout, even if EAGAIN was raised

Bugfixes (win32):

- [#27] fix race condition in ``read()``, fix minimal timeout issue
- race condition in nonblocking case
- [#49] change exception type in case SetCommState fails
- [#50] fixed issue with 0 timeout on windows 10


Version 3.0.1   2016-01-11
--------------------------
- special case for FDTIBUS in list_ports on win32 (#61)

Bugfixes:

- ``Serial`` keyword arguments, more on backward compatibility, fix #55
- list_ports: return name if product is None, fix for #54
- port_publisher: restore some sorting of ports


Version 3.1.0   2016-05-27
--------------------------
Improvements:

- improve error handling in ``alt://`` handler
- ``socket://`` internally used select, improves timeout behavior
- initial state of RTS/DTR: ignore error when setting on open posix
  (support connecting to pty's)
- code style updates
- posix: remove "number_to_device" which is not called anymore
- add cancel_read and cancel_write to win32 and posix implementations

Bugfixes:

- [#68] aio: catch errors and close connection
- [#87] hexlify: update codec for Python 2
- [#100] setPort not implemented
- [#101] bug in serial.threaded.Packetizer with easy fix
- [#104] rfc2217 and socket: set timeout in create_connection
- [#107] miniterm.py fails to exit on failed serial port

Bugfixes (posix):

- [#59] fixes for RTS/DTR handling on open
- [#77] list_ports_osx: add missing import
- [#85] serialposix.py _set_rs485_mode() tries to read non-existing
  rs485_settings.delay_rts_before_send
- [#96] patch: native RS485 is never enabled

Bugfixes (win32):

- fix bad super call and duplicate old-style __init__ call
- [#80] list_ports: Compatibility issue between Windows/Linux


Version 3.1.1   2016-06-12
--------------------------
Improvements:

- deprecate ``nonblocking()`` method on posix, the port is already in this
  mode.
- style: use .format() in various places instead of "%" formatting

Bugfixes:

- [#122] fix bug in FramedPacket
- [#127] The Serial class in the .NET/Mono (IronPython) backend does not
  implement the _reconfigure_port method
- [#123, #128] Avoid Python 3 syntax in aio module

Bugfixes (posix):

- [#126] PATCH: Check delay_before_tx/rx for None in serialposix.py
- posix: retry if interrupted in Serial.read

Bugfixes (win32):

- win32: handle errors of GetOverlappedResult in read(), fixes #121


Version 3.2.0   2016-10-14
--------------------------
See 3.2.1, this one missed a merge request related to removing aio.


Version 3.2.1   2016-10-14
--------------------------
Improvements:

- remove ``serial.aio`` in favor of separate package, ``pyserial-asyncio``
- add client mode to example ``tcp_serial_redirect.py``
- use of monotonic clock for timeouts, when available (Python 3.3 and up)
- [#169] arbitrary baud rate support for BSD family
- improve tests, improve ``loop://``

Bugfixes:

- [#137] Exception while cancel in miniterm (python3)
- [#143] Class Serial in protocol_loop.py references variable before assigning
  to it
- [#149] Python 3 fix for threaded.FramedPacket

Bugfixes (posix):

- [#133] _update_dtr_state throws Inappropriate ioctl for virtual serial
  port created by socat on OS X
- [#157] Broken handling of CMSPAR in serialposix.py

Bugfixes (win32):

- [#144] Use Unicode API for list_ports
- [#145] list_ports_windows: support devices with only VID
- [#162] Write in non-blocking mode returns incorrect value on windows


Version 3.2.x   2017-xx-xx
--------------------------

Bugfixes (win32):

- [#194] spurious write fails with ERROR_SUCCESS
