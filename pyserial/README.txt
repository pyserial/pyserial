pySerial
--------
This module capsulates the access for the serial port. It provides backends
for stadard Python running on Windows, Linux, BSD (possibly any POSIX
compilant system) and Jython. The module named "serial" automaticaly selects
the appropriate backed.

It is released under a free software license, see LICENSE.txt for more
details.

(C) 2001-2002 Chris Liechti <cliechti@gmx.net>


Features
--------
- same class based interface on all supported platforms
- port numbering starts at zero, no need to know the port name in the user
  program
- port string can be specified if access through numbering is inappropriate
- support for diffrent bytesizes, stopbits, parity and flow control
  with RTS/CTS and/or xon/xoff
- working with or without receive timeout
- file like API with "read" and "write"
- The files in this package are 100% pure Python.
  They depend on non standard but common packages on Windows (win32all) and
  Jython (JavaComm). POSIX (Linux, BSD) uses only modules from the standard
  python distribution)
- The port is set up for binary transmission. No NULL byte stripping, CR-LF
  translation etc. (which are many times enabled for POSIX.) This makes this
  module universally useful.


Requirements
------------
- Python 2.0 or newer (1.5.2 untested)
- win32all extensions on Windows
- "Java Communications" (JavaComm) extension for Java/Jython


Installation
------------
Extract files from the archive, open a shell/console in that directory and
let Disutils do the rest: "python setup.py install"

The files get installed in the "Lib/site-packages" directory in newer
Python versions.


Short introduction
------------------
import serial
#open port 0 at 9600,8,N,1, no timeout
ser = serial.Serial(0)
ser.write("hello")  #write a string
ser.close()

#open port at 19200,8,N,1, 1s timeout
ser = serial.Serial('/dev/ttyS1', 19200, timeout=1)
x = ser.read()      #read one byte
s = ser.read(10)    #read up to ten bytes (timeout)
ser.close()

Parameters for the Serial class
-------------------------------
ser = serial.Serial(
    port,                   #number of device, numbering starts at
                            #zero. if everything fails, the user
                            #can specify a device string, note
                            #that this isn't portable anymore
    baudrate=9600,          #baudrate
    bytesize=EIGHTBITS,     #number of databits
    parity=PARITY_NONE,     #enable parity checking
    stopbits=STOPBITS_ONE,  #number of stopbits
    timeout=None,           #set a timeout value, None for waiting forever
    xonxoff=0,              #enable software flow control
    rtscts=0,               #enable RTS/CTS flow control
)

Constants
---------
parity:
    serial.PARITY_NONE
    serial.PARITY_EVEN
    serial.PARITY_ODD
stopbits:
    serial.STOPBITS_ONE
    serial.STOPBITS_TWO
bytesize:
    serial.FIVEBITS
    serial.SIXBITS
    serial.SEVENBITS
    serial.EIGHTBITS


References
----------
- Python: http://www.python.org
- Jython: http://www.jython.org
- win32all: http://starship.python.net/crew/mhammond/
  and http://www.activestate.com/Products/ActivePython/win32all.html
- Java@IBM http://www-106.ibm.com/developerworks/java/jdk/
  (JavaComm links are on the download page for the respecive platform jdk)
- Java@SUN http://java.sun.com/products/
