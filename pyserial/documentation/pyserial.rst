==========
 pySerial
==========

Overview
========
This module encapsulates the access for the serial port. It provides backends
for Python running on Windows, Linux, BSD (possibly any POSIX compliant
system), Jython and IronPython (.NET and Mono). The module named "serial"
automatically selects the appropriate backend.

It is released under a free software license, see LICENSE_ for more
details.

Copyright (C) 2001-2013 Chris Liechti <cliechti(at)gmx.net>

Other pages (online)

- `project page on SourceForge`_
- `SVN repository`_
- `Download Page`_ with releases (PyPi)
- This page, when viewed online is at http://pyserial.sf.net.

.. _LICENSE: appendix.html#license
.. _`project page on SourceForge`: http://sourceforge.net/projects/pyserial/
.. _`SVN repository`: http://svn.code.sf.net/p/pyserial/code/trunk
.. _`Download Page`: http://pypi.python.org/pypi/pyserial


Features
========
- Same class based interface on all supported platforms.
- Access to the port settings through Python properties.
- Support for different byte sizes, stop bits, parity and flow control with
  RTS/CTS and/or Xon/Xoff.
- Working with or without receive timeout.
- File like API with "read" and "write" ("readline" etc. also supported).
- The files in this package are 100% pure Python.
- The port is set up for binary transmission. No NULL byte stripping, CR-LF
  translation etc. (which are many times enabled for POSIX.) This makes this
  module universally useful.
- Compatible with :mod:`io` library (Python 2.6+)
- RFC 2217 client (experimental), server provided in the examples.


Requirements
============
- Python 2.3 or newer, including Python 3.x
- ctypes extension on Windows (is in standard library since Python 2.5+)
- "Java Communications" (JavaComm) or compatible extension for Java/Jython


Installation
============

pyserial
--------
This installs a package that can be used from Python (``import serial``).

To install for all users on the system, administrator rights (root)
may be required.

From PyPI
~~~~~~~~~
pySerial can be installed from PyPI, either manually downloading the
files and installing as described below or using::

    pip install pyserial

or::

    easy_install -U pyserial

From source (tar.gz or checkout)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Download the archive from http://pypi.python.org/pypi/pyserial.
Unpack the archive, enter the ``pyserial-x.y`` directory and run::

    python setup.py install

For Python 3.x::

    python3 setup.py install

Packages
~~~~~~~~
There are also packaged versions for some Linux distributions and Windows:

Debian/Ubuntu
    A package is available under the name "python-serial". Note that some
    distributions may package an older version of pySerial.

Windows
    There is also a Windows installer for end users. It is located in the
    PyPi_.  Developers also may be interested to get the source archive,
    because it contains examples, tests and the this documentation.

.. _PyPi: http://pypi.python.org/pypi/pyserial


References
==========
* Python: http://www.python.org/
* Jython: http://www.jython.org/
* Java@IBM: http://www-106.ibm.com/developerworks/java/jdk/ (JavaComm links are
  on the download page for the respective platform JDK)
* Java@SUN: http://java.sun.com/products/
* IronPython: http://www.codeplex.com/IronPython
* setuptools: http://peak.telecommunity.com/DevCenter/setuptools


Older Versions
==============
Older versions are still available in the old download_ page. pySerial 1.21
is compatible with Python 2.0 on Windows, Linux and several un*x like systems,
MacOSX and Jython.

On windows releases older than 2.5 will depend on pywin32_ (previously known as
win32all)

.. _download: http://sourceforge.net/projects/pyserial/files/pyserial/
.. _pywin32: http://pypi.python.org/pypi/pywin32
