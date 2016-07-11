==========
 Appendix
==========

How To
======

Enable :rfc:`2217` in programs using pySerial.
    Patch the code where the :class:`serial.Serial` is instantiated. Replace
    it with::

        try:
            s = serial.serial_for_url(...)
        except AttributeError:
            s = serial.Serial(...)

    Assuming the application already stores port names as strings that's all
    that is required. The user just needs a way to change the port setting of
    your application to an ``rfc2217://`` :ref:`URL <URLs>` (e.g. by editing a
    configuration file, GUI dialog etc.).

    Please note that this enables all :ref:`URL <URLs>` types supported by
    pySerial and that those involving the network are unencrypted and not
    protected against eavesdropping.

Test your setup.
    Is the device not working as expected? Maybe it's time to check the
    connection before proceeding. :ref:`miniterm` from the :ref:`examples`
    can be used to open the serial port and do some basic tests.

    To test cables, connecting RX to TX (loop back) and typing some characters
    in :ref:`miniterm` is a simple test. When the characters are displayed
    on the screen, then at least RX and TX work (they still could be swapped
    though).


FAQ
===
Example works in :ref:`miniterm` but not in script.
    The RTS and DTR lines are switched when the port is opened. This may cause
    some processing or reset on the connected device. In such a cases an
    immediately following call to :meth:`write` may not be received by the
    device.

    A delay after opening the port, before the first :meth:`write`, is
    recommended in this situation. E.g. a ``time.sleep(1)``


Application works when .py file is run, but fails when packaged (py2exe etc.)
    py2exe and similar packaging programs scan the sources for import
    statements and create a list of modules that they package. pySerial may
    create two issues with that:

    - implementations for other modules are found. On Windows, it's safe to
      exclude 'serialposix', 'serialjava' and 'serialcli' as these are not
      used.

    - :func:`serial.serial_for_url` does a dynamic lookup of protocol handlers
      at runtime.  If this function is used, the desired handlers have to be
      included manually (e.g. 'serial.urlhandler.protocol_socket',
      'serial.urlhandler.protocol_rfc2217', etc.). This can be done either with
      the "includes" option in ``setup.py`` or by a dummy import in one of the
      packaged modules.

User supplied URL handlers
    :func:`serial.serial_for_url` can be used to access "virtual" serial ports
    identified by an :ref:`URL <URLs>` scheme. E.g. for the :rfc:`2217`:
    ``rfc2217://``.

    Custom :ref:`URL <URLs>` handlers can be added by extending the module
    search path in :data:`serial.protocol_handler_packages`. This is possible
    starting from pySerial V2.6.

``Permission denied`` errors
    On POSIX based systems, the user usually needs to be in a special group to
    have access to serial ports.

    On Debian based systems, serial ports are usually in the group ``dialout``,
    so running ``sudo adduser $USER dialout`` (and logging-out and -in) enables
    the user to access the port.


Related software
================

com0com - http://com0com.sourceforge.net/
    Provides virtual serial ports for Windows.


License
=======
Copyright (c) 2001-2016 Chris Liechti <cliechti@gmx.net>
All Rights Reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

  * Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

  * Redistributions in binary form must reproduce the above
    copyright notice, this list of conditions and the following
    disclaimer in the documentation and/or other materials provided
    with the distribution.

  * Neither the name of the copyright holder nor the names of its
    contributors may be used to endorse or promote products derived
    from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

