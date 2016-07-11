==========
 pySerial
==========

Overview
========

This module encapsulates the access for the serial port. It provides backends
for Python_ running on Windows, OSX, Linux, BSD (possibly any POSIX compliant
system) and IronPython. The module named "serial" automatically selects the
appropriate backend.

It is released under a free software license, see LICENSE_ for more
details.

Copyright (C) 2001-2016 Chris Liechti <cliechti(at)gmx.net>

Other pages (online)

- `project page on GitHub`_
- `Download Page`_ with releases (PyPi)
- This page, when viewed online is at https://pyserial.readthedocs.io/en/latest/ or
  http://pythonhosted.org/pyserial/ .

.. _Python: http://python.org/
.. _LICENSE: appendix.html#license
.. _`project page on GitHub`: https://github.com/pyserial/pyserial/
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
- Compatible with :mod:`io` library
- RFC 2217 client (experimental), server provided in the examples.


Requirements
============
- Python 2.7 or newer, including Python 3.4 and newer
- "Java Communications" (JavaComm) or compatible extension for Java/Jython


Installation
============

pySerial
--------
This installs a package that can be used from Python (``import serial``).

To install for all users on the system, administrator rights (root)
may be required.

From PyPI
~~~~~~~~~
pySerial can be installed from PyPI::

    python -m pip install pyserial

Using the `python`/`python3` executable of the desired version (2.x/3.x).

From source (tar.gz or checkout)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Download the archive from http://pypi.python.org/pypi/pyserial or
https://github.com/pyserial/pyserial/releases.
Unpack the archive, enter the ``pyserial-x.y`` directory and run::

    python setup.py install

Using the `python`/`python3` executable of the desired version (2.x/3.x).

Packages
~~~~~~~~
There are also packaged versions for some Linux distributions and Windows:

Debian/Ubuntu
    A package is available under the name "python-serial" or similar. Note
    that some distributions may package an older version of pySerial.

Windows
    There is a "wheel" file for end users. It is located in the PyPi_.
    Developers also may be interested to get the source archive,
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

On Windows, releases older than 2.5 will depend on pywin32_ (previously known as
win32all)

.. _download: https://pypi.python.org/pypi/pyserial
.. _pywin32: http://pypi.python.org/pypi/pywin32
