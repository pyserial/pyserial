pyParallel
--------
This module capsulates the access for the parallel port. It provides backends
for standard Python running on Windows, Linux, BSD and Jython.
The module named "parallel" automaticaly selects the appropriate backend.

It is released under a free software license, see LICENSE.txt for more
details.

Project Homepage: pyserial.sourceforge.net
(C) 2002 Chris Liechti <cliechti@gmx.net>


Features
--------
- same class based interface on all supported platforms
- port numbering starts at zero, no need to know the platform dependant port
  name in the user program
- port name can be specified if access through numbering is inappropriate

Requirements
------------
- Python 2.0 or newer (1.5.2 untested)
- "Java Communications" (JavaComm) extension for Java/Jython


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
