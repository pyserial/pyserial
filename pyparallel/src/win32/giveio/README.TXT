The entire archive was pulled from here:
Dr. Dobb's Journal, http://www.ddj.com/ftp/1996/1996.05/directio.zip
It contained some other snippets too, but as they are not useful here
I don't include them here.

chris

Following is the original readme of the archive:
-----------------------------------------------------------------------------


Author: Dale Roberts, Direct I/O and Windows NT


Here are two helpful hints to get you going with GIVEIO.  The first
section below mentions the INSTDRV utility that is provided with the
Microsoft DDK. If you do not have access to the DDK, you can use Paula
Tomlinson's program LOADDRV instead.  She describes it in her May 1995
article in Windows/DOS Developer's Journal (now Windows Developer's
Journal).  You can get the program from their FTP site at:

   ftp://ftp.mfi.com/pub/windev/1995/may95.zip.


------------------------------------------------------------------
Device Driver Installation Made Easy

The Microsoft NT Device Driver Kit documentation implies in several 
places that there are several steps involved in installing a device driver 
and making it accessible to a Win32 application.  It explains that you 
should edit the registry manually and then reboot the system.  But 
device drivers are dynamically loadable and unloadable in NT, and the 
DDK comes with a very handy utility called INSTDRV that 
demonstrates this facility in a very practical manner.

INSTDRV is a console application that will register, load, and start a 
kernel mode device driver.  It does not require you to edit the registry 
manually or reboot the computer.  On the command line you simply 
give the name of your device driver and the complete path to the .SYS 
file (which does not need to be in the system's DRIVERS directory).  
After this command is executed, you will find that the driver has been 
registered with the system and appears in the Devices applet in the 
control panel.  If you give the word remove instead of the path, the 
driver is removed from the system and taken out of the driver database.

Once the driver is loaded and started, you can use the control panel's 
Devices applet to start and stop it, or you can use the net start and net 
stop commands (these are much faster) from a console window.  When 
a kernel mode device is stopped, it is in also unloaded from memory.  
The next time you start the device, a fresh copy of the driver is read 
from the hard drive, if it has been modified.  This makes it very 
convenient to develop device drivers, since you can go through the 
modify, stop, start cycle repeatedly without ever needing to reboot.  If 
you need your driver to load at boot time, you can go into the Devices 
applet and change its startup mode to boot.

The other component that is needed to make the driver visible to user 
mode applications, so they can use CreateFile() calls to access the 
driver, is registering the name in the DOS Devices name space.  This 
can be done, as documented in the DDK, by editing the registry 
manually and rebooting.  Or, much more simply, the kernel mode 
driver can call the IoCreateSymbolicLink() function to register the 
name itself.  The GIVEIO driver shown in Listing Four uses the later 
technique.  Once the name is registered, user mode applications can get 
a file handle to the device driver by calling CreateFile() with the driver 
name as the file parameter, but preceding the driver name with the 
special cookie \\.\.  The TESTIO application in Listing Five uses this 
technique.

------------------------------------------------------------------
Quick Trick:  Using DEBUG With Port I/O

Sometimes you just need to do a quick I/O operation to a port.  In DOS, 
you could use the DEBUG program to accomplish this.  In NT, once 
you have the GIVEIO device driver up and running, you can once 
again use DEBUG for port I/O.  If you look at the source code for the 
test application, you'll see that all it does is open and close the GIVEIO 
device driver.  It uses the special cookie \\.\ before the driver name in 
order to access it.  Without modifying DEBUG, you can have it open 
this device driver by simply typing debug \\.\giveio in an NT console 
window.  You will get an error message complaining that the file 
\\.\giveio is not found, but it will give DEBUG I/O access anyway.  
Subsequent DOS applications that are run from this console window 
will also have I/O access.

WIN32 applications executed from this console window will still cause 
exceptions.  This is because DEBUG (and any other DOS application) 
runs in the context of the VDM (Virtual DOS Machine) process of the 
console box, whereas each WIN32 application gets its own process.  
The VDM process stays active as long as the console window is open, 
but each WIN32 application creates a brand new process with the 
IOPM offset initialized to point beyond the end of the TSS.
