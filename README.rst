=================
 pySerial  |docs|
=================

Overview
========
This module encapsulates the access for the serial port. It provides backends
for Python_ running on Windows, OSX, Linux, and BSD (possibly any POSIX compliant
system). The module named "serial" automatically selects the
appropriate backend.

- Project Homepage: https://github.com/pyserial/pyserial
- Download Page: https://pypi.org/project/pyserial/

BSD license, (C) 2001-2020 Chris Liechti <cliechti@gmx.net>


Documentation
=============
For API documentation, usage and examples see files in the "documentation"
directory.  The ".rst" files can be read in any text editor or being converted to
HTML or PDF using Sphinx_. An HTML version is online at
https://pyserial.readthedocs.io/en/latest/

Examples
========
Examples and unit tests are in the directory examples_.


Installation
============
``pip install pyserial`` should work for most users.

Detailed information can be found in `documentation/pyserial.rst`_.

Windows installers are also available (see download link above).

or

To install this package with conda run:   

``conda install -c conda-forge pyserial``   

conda builds are available for linux, mac and windows.

.. _`documentation/pyserial.rst`: https://github.com/pyserial/pyserial/blob/master/documentation/pyserial.rst#installation
.. _examples: https://github.com/pyserial/pyserial/blob/master/examples
.. _Python: https://www.python.org/
.. _Sphinx: https://www.sphinx-doc.org/
.. |docs| image:: https://readthedocs.org/projects/pyserial/badge/?version=latest
   :target: https://pyserial.readthedocs.io/
   :alt: Documentation
