pyParallel
--------
This module encapsulates the access for the parallel port. It provides
backends for standard Python running on Windows and Linux.

It is released under a free software license, see LICENSE.txt for more
details.

Project Homepage: pyserial.sourceforge.net
(C) 2002 Chris Liechti <cliechti@gmx.net>


Features
--------
- same class based interface on all supported platforms

Requirements
------------
- Python 2.0 or newer (1.5.2 untested)

Installation
------------
Extract files from the archive, open a shell/console in that directory and
let Distutils do the rest: "python setup.py install"

The files get installed in the "Lib/site-packages" directory in newer
Python versions.


Short introduction
------------------
>>> import parallel
>>> p = parallel.Parallel()     #open LPT1
>>> p.setData(0x55)

References
----------
- Python: http://www.python.org
- Jython: http://www.jython.org
