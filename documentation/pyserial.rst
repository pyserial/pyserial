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
- Python 2.7 or Python 3.4 and newer

- If running on Windows: Windows 7 or newer

- If running on Jython: "Java Communications" (JavaComm) or compatible
  extension for Java

For older installations (older Python versions or older operating systems), see
`older versions`_ below.


Installation
============

This installs a package that can be used from Python (``import serial``).

To install for all users on the system, administrator rights (root)
may be required.

From PyPI
---------
pySerial can be installed from PyPI::

    python -m pip install pyserial

Using the `python`/`python3` executable of the desired version (2.7/3.x).

Developers also may be interested to get the source archive, because it
contains examples, tests and the this documentation.

From Conda
----------
pySerial can be installed from Conda::

    conda install pyserial
    
    or
    
    conda install -c conda-forge pyserial
    
Currently the default conda channel will provide version 3.4 whereas the
conda-forge channel provides the current 3.x version.

Conda: https://www.continuum.io/downloads

From source (zip/tar.gz or checkout)
------------------------------------
Download the archive from http://pypi.python.org/pypi/pyserial or
https://github.com/pyserial/pyserial/releases.
Unpack the archive, enter the ``pyserial-x.y`` directory and run::

    python setup.py install

Using the `python`/`python3` executable of the desired version (2.7/3.x).

Packages
--------
There are also packaged versions for some Linux distributions:

- Debian/Ubuntu: "python-serial", "python3-serial"
- Fedora / RHEL / CentOS / EPEL: "pyserial"
- Arch Linux: "python-pyserial"
- Gentoo: "dev-python/pyserial"

Note that some distributions may package an older version of pySerial.
These packages are created and maintained by developers working on
these distributions.

.. _PyPi: http://pypi.python.org/pypi/pyserial


References
==========
* Python: http://www.python.org/
* Jython: http://www.jython.org/
* IronPython: http://www.codeplex.com/IronPython


Older Versions
==============
Older versions are still available on the current download_ page or the `old
download`_ page. The last version of pySerial's 2.x series was `2.7`_,
compatible with Python 2.3 and newer and partially with early Python 3.x
versions.

pySerial `1.21`_ is compatible with Python 2.0 on Windows, Linux and several
un*x like systems, MacOSX and Jython.

On Windows, releases older than 2.5 will depend on pywin32_ (previously known as
win32all). WinXP is supported up to 3.0.1.


.. _`old download`: https://sourceforge.net/projects/pyserial/files/pyserial/
.. _download: https://pypi.python.org/simple/pyserial/
.. _pywin32: http://pypi.python.org/pypi/pywin32
.. _`2.7`: https://pypi.python.org/pypi/pyserial/2.7
.. _`1.21`: https://sourceforge.net/projects/pyserial/files/pyserial/1.21/pyserial-1.21.zip/download
