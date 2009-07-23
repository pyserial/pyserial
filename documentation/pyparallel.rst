============
 pyParallel
============

.. note:: This module is in development (since years ;-)

Overview
========
This module encapsulates the access for the parallel port. It provides backends
for Python running on Windows and Linux. Other platforms are possible too but
not yet integrated.

This module is still under development. But it may be useful for developers.

Copyright (C) 2001-2003 Chris Liechti <cliechti(at)gmx.net>

Here is the `project page on SourceForge`_ and here is the `SVN repository`_.

.. _`project page on SourceForge`: http://sourceforge.net/projects/pyserial/
.. _`SVN repository`: http://sourceforge.net/svn/?group_id=46487


Features
--------
* same class based interface on all supported platforms
* port numbering starts at zero, no need to know the port name in the user program
* port string (device name) can be specified if access through numbering is inappropriate


Requirements
------------
* Python 2.2 or newer
* "Java Communications" (JavaComm) extension for Java/Jython


Installation
------------
Extract files from the archive, open a shell/console in that directory and let
Distutils do the rest: ``python setup.py install``

The files get installed in the "Lib/site-packages" directory in newer Python versions.

The windows version needs a compiled extension and the giveio.sys driver for
Windows NT/2k/XP. The extension module can be compiled with Distutils with
either MSVC or GCC/mingw32.

It is released under a free software license, see LICENSE.txt for more details.


Short introduction
==================
::

    >>> import parallel
    >>> p = parallel.Parallel()     # open LPT1
    >>> p.setData(0x55)


Examples
--------
Please look in the SVN Repository. There is an example directory where you can
find a simple terminal and more.
http://pyserial.svn.sourceforge.net/viewvc/pyserial/trunk/pyparallel/examples/


API
===

.. module:: parallel

.. class:: Parallel

    .. method:: __init__(port)

        Open given parallel port.

    .. method:: setData(value)

        Apply the given byte to the data pins of the parallel port.

    .. method:: setDataStrobe(level)

        Set the "data strobe" line to the given state.

    .. method:: setAutoFeed(level)

        Set "auto feed" line to given state.

    .. method:: setInitOut(level)

        Set "initialize" line to given state.

    .. method: setSelect(level)

        Set "select" line to given state.

    .. method:getInError()

        Set "Error" line to given state.

    .. method:: getInSelected()

        Read level of "select" line.

    .. method:: getInPaperOut()

        Read level of "paper out" line.

    .. method:: getInAcknowledge()

        Read level of "Acknowledge" line.

    .. method: getInBusy()

        Read level of "busy" line.


.. module:: parallel.parallelutil

.. class:: BitaccessMeta

    This mix-in class adds a few properties that allow easier bit access to the
    data lines. (D0 .. D7) e.g. p.D0 refers to the first bit of the data
    lines.

.. class:: VirtualParallelPort

    This class provides a virtual parallel port implementation, useful
    for tests and simulations without real hardware.


Notes
=====

Linux
-----
1. The :manpage:`lp(4)` module must be unloaded, ``rmmod lp``. ``lp`` claims
   exclusive access to the port and other programs won't be able to use it.

2. The :manpage:`ppdev(4)` module needs to be loaded, ``modprobe ppdev``. When
   ``udev`` is in use, (default with 2.6 kernels) this will create a
   ``/dev/parport0``.

3. The user needs to have write permissions to ``/dev/parport0``. Many
   distributions have an ``lp`` group that owns the device; the simplest is to
   add the user account to this group. Simply changing permissions on the
   device is not the best strategy as they will be reverted to their defaults
   next time the driver is loaded.


Windows
-------
The giveio driver must be installed as the module needs direct access to the
hardware. This also means that USB parallel port adapters won't be supported.


Misc
====
References
----------
* Python: http://www.python.org/
* Jython: http://www.jython.org/
* Java@IBM: http://www-106.ibm.com/developerworks/java/jdk/ (JavaComm links are
  on the download page for the respective platform JDK)
* Java@SUN: http://java.sun.com/products/
