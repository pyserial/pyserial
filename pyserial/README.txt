pySerial
--------
This module capsulates the access for the serial port. It provides backends
for standard Python running on Windows, Linux, BSD (possibly any POSIX
compilant system) and Jython. The module named "serial" automaticaly selects
the appropriate backend.

It is released under a free software license, see LICENSE.txt for more
details.

Project Homepage: pyserial.sourceforge.net
(C) 2001-2003 Chris Liechti <cliechti@gmx.net>


Features
--------
- same class based interface on all supported platforms
- port numbering starts at zero, no need to know the platform dependant port
  name in the user program
- port name can be specified if access through numbering is inappropriate
- support for different bytesizes, stopbits, parity and flow control
  with RTS/CTS and/or xon/xoff
- working with or without receive timeout, blocking or non-blocking
- file like API with "read" and "write" ("readline" etc. also supported)
- The files in this package are 100% pure Python.
  They depend on non standard but common packages on Windows (win32all) and
  Jython (JavaComm). POSIX (Linux, BSD) uses only modules from the standard
  Python distribution)
- The port is set up for binary transmission. No NULL byte stripping, CR-LF
  translation etc. (which are many times enabled for POSIX.) This makes this
  module universally useful.


Requirements
------------
- Python 2.2 or newer
- win32all extensions on Windows
- "Java Communications" (JavaComm) extension for Java/Jython


Installation
------------
Extract files from the archive, open a shell/console in that directory and
let Distutils do the rest: "python setup.py install"

The files get installed in the "Lib/site-packages" directory.

Serial to USB adapters
----------------------
Such adapters are reported to work under Mac OSX and Windows. They are
mapped to a normal COM port under Windows, but on Mac OSX and other platforms
they have special device names.

Mac OSX: "/dev/[cu|tty].USA<adaptername><USB-part>P<serial-port>.1"
    e.g. "/dev/cu.USA19QW11P1.1"

Linux: "/dev/usb/ttyUSB[n]" or "/dev/ttyUSB[n]"
    first for for RedHat, second form for Debian.
    e.g. "/dev/usb/ttyUSB0"

Either use these names for the serial ports or create a link to the common device
names like "ln -s /dev/cu.USA19QW11P1.1 /dev/cuaa0" or "ln -s /dev/usb/ttyUSB0
/dev/ttyS4" etc.

But be aware that the (USB) device file disappears as soon as you unplug the USB
adapter.


Short introduction
------------------
Open port 0 at "9600,8,N,1", no timeout
>>> import serial
>>> ser = serial.Serial(0)  #open first serial port
>>> print ser.portstr       #check which port was realy used
>>> ser.write("hello")      #write a string
>>> ser.close()             #close port

Open named port at "19200,8,N,1", 1s timeout
>>> ser = serial.Serial('/dev/ttyS1', 19200, timeout=1)
>>> x = ser.read()          #read one byte
>>> s = ser.read(10)        #read up to ten bytes (timeout)
>>> line = ser.readline()   #read a '\n' terminated line
>>> ser.close()

Open second port at "38400,8,E,1", non blocking HW handshaking
>>> ser = serial.Serial(1, 38400, timeout=0,
...                     parity=serial.PARITY_EVEN, rtscts=1)
>>> s = ser.read(100)       #read up to one hunded bytes
...                         #or as much is in the buffer

Get a Serial instance and configure/open it later
>>> ser = serial.Serial()
>>> ser.baudrate = 19200
>>> ser.port = 0
>>> ser
Serial<id=0xa81c10, open=False>(port='COM1', baudrate=19200, bytesize=8,
parity='N', stopbits=1, timeout=None, xonxoff=0, rtscts=0)
>>> ser.open()
>>> ser.isOpen()
True
>>> ser.close()
>>> ser.isOpen()
False

Be carefully when using "readline". Do specify a timeout when
opening the serial port otherwise it could block forever if
no newline character is received. Also note that "readlines" only
works with a timeout. "readlines" depends on having a timeout
and interprets that as EOF (end of file). It raises an exception
if the port is not opened correctly.


Parameters for the Serial class
-------------------------------
ser = serial.Serial(
    port=None,              #number of device, numbering starts at
                            #zero. if everything fails, the user
                            #can specify a device string, note
                            #that this isn't portable anymore
                            #if no port is specified an unconfigured
                            #an closed serial port object is created
    baudrate=9600,          #baudrate
    bytesize=EIGHTBITS,     #number of databits
    parity=PARITY_NONE,     #enable parity checking
    stopbits=STOPBITS_ONE,  #number of stopbits
    timeout=None,           #set a timeout value, None to wait forever
    xonxoff=0,              #enable software flow control
    rtscts=0,               #enable RTS/CTS flow control
)

The port is immediately opened on object creation.
Options for read timeout:
timeout=None            #wait forever
timeout=0               #non-blocking mode (return immediately on read)
timeout=x               #set timeout to x seconds (float allowed)

Methods of Serial instances
---------------------------
open()                  #open port
close()                 #close port immediately
setBaudrate(baudrate)   #change baudarte on an open port
inWaiting()             #return the number of chars in the receive buffer
read(size=1)            #read "size" characters
write(s)                #write the string s to the port
flushInput()            #flush input buffer, discarding all it's contents
flushOutput()           #flush output buffer, abort output
sendBreak()             #send break condition
setRTS(level=1)         #set RTS line to specified logic level
setDTR(level=1)         #set DTR line to specified logic level
getCTS()                #return the state of the CTS line
getDSR()                #return the state of the DSR line
getRI()                 #return the state of the RI line
getCD()                 #return the state of the CD line

Attributes of Serial instances
------------------------------
Read Only:
portstr                 #device name
BAUDRATES               #list of valid baudrates
BYTESIZES               #list of valid byte sizes
PARITIES                #list of valid parities
STOPBITS                #list of valid stop bit widths

New values can be assigned to the following attribues, the port
will be reconfigured, even if it's opened at that time:
port                    #port name/number as set by the user
baudrate                #current baudrate setting
bytesize                #bytesize in bits
parity                  #parity setting
stopbits                #stop bit with (1,2)
timeout                 #timeout setting
xonxoff                 #if XonXoff flow control is enabled
rtscts                  #if hardware flow control is enabled


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

Tips & Tricks
-------------
- Some protocols need CR LF ("\r\n") as line terminator, not just LF ("\n").
  Telephone modems with the AT command set are an example of this behaviour.

- Scanning for available serial ports is possible with more or less sucess on
  some platforms. Look at the tools from Roger Binns:
  http://cvs.sourceforge.net/cgi-bin/viewcvs.cgi/bitpim/comscan/

References
----------
- Python: http://www.python.org
- Jython: http://www.jython.org
- win32all: http://starship.python.net/crew/mhammond/
  and http://www.activestate.com/Products/ActivePython/win32all.html
- Java@IBM http://www-106.ibm.com/developerworks/java/jdk/
  (JavaComm links are on the download page for the respective platform jdk)
- Java@SUN http://java.sun.com/products/
