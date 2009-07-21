==========
 pySerial
==========

Overview
========
This module encapsulates the access for the serial port. It provides backends
for Python running on Windows, Linux, BSD (possibly any POSIX compliant
system), Jython and IronPython (.NET and Mono). The module named "serial"
automatically selects the appropriate backend.

It is released under a free software license, see LICENSE.txt_ for more
details.

  (C) 2001-2009 Chris Liechti <cliechti@gmx.net>

The `project page on SourceForge`_ and here is the `SVN repository`_ and the `Download Page`_.

The homepage is at http://pyserial.sf.net.

.. _LICENSE.txt: http://pyserial.svn.sourceforge.net/viewvc/*checkout*/pyserial/trunk/pyserial/LICENSE.txt
.. _`project page on SourceForge`: http://sourceforge.net/projects/pyserial/
.. _`SVN repository`: http://sourceforge.net/svn/?group_id=46487
.. _`Download Page`: http://sourceforge.net/project/showfiles.php?group_id=46487


Features
========
* same class based interface on all supported platforms
* access to the port settings through Python 2.2+ properties
* port numbering starts at zero, no need to know the port name in the user
  program
* port string (device name) can be specified if access through numbering is
  inappropriate
* support for different bytesizes, stopbits, parity and flow control with
  RTS/CTS and/or Xon/Xoff
* working with or without receive timeout
* file like API with "read" and "write" ("readline" etc. also supported)
* The files in this package are 100% pure Python. They depend on non standard
  but common packages on Windows (pywin32) and Jython (JavaComm). POSIX (Linux,
  BSD) uses only modules from the standard Python distribution)
* The port is set up for binary transmission. No NULL byte stripping, CR-LF
  translation etc. (which are many times enabled for POSIX.) This makes this
  module universally useful.


Requirements
============
* Python 2.2 or newer
* pywin32 extensions on Windows
* "Java Communications" (JavaComm) or compatible extension for Java/Jython

Installation
============

pyserial
--------
This installs a package that can be used from python (``import serial``).

The Python pywin32 library needs to be installed on windows.

To install the module for all users on the system, administrator rights (root)
is required..

From source (tar.gz or checkout)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
http://pypi.python.org/pypi/pyserial
Unpack the archive, enter the ``pyserial-x.y`` directory and run::

    python setup.py install

Setuptools/PyPI
~~~~~~~~~~~~~~~
Alternatively it can be installed from PyPy, either manually downloading the
files and installing as described above or using::

    easy_install -U pyserial

Packages
~~~~~~~~
There are also packaged versions for some Linux distributions and Windows:

Debian/Ubuntu
    A package is availabe under the name "python-serial"

Windows
    There is also a Windows installer for end users. It is located in the
    PyPi_.  Developers may be interested to get the source archive, because it
    contains examples and the readme.

.. _PyPi: http://pypi.python.org/pypi/pyserial


References
==========
* Python: http://www.python.org/|http://www.python.org
* pywin32: http://sourceforge.net/projects/pywin32/ (previously known as win32all)
* Jython: http://www.jython.org/|http://www.jython.org
* Java@IBM http://www-106.ibm.com/developerworks/java/jdk/ (JavaComm links are on the download page for the respective platform jdk)
* Java@SUN http://java.sun.com/products/
* IronPython: http://www.codeplex.com/IronPython
* setuptools: http://peak.telecommunity.com/DevCenter/setuptools


Older Versions
==============
Older versions are still available on the `Download Page`_. pySerial 1.21 is
compatible with Python 2.0 on Windows, Linux and several un*x like systems,
MacOSX and Jython.

.. _`Download Page`: http://sourceforge.net/project/showfiles.php?group_id=46487
