New:
simpleio.c provides inp(), outp(), init() these functions are accessed trough
ctypes.

Build (cygwin/mingw): run "make" the makfile should care of everything.

- - - - - - - - - - - - -
Old python extension:

This extension is needed on Windows as there is no API to
manipulate the parallel port. This Python extension exposes
"inp()" and "outp()" that can be used to manipulate the printer
IOs directly. It could be basicaly used to access any IO port.

On Windows NT/2k/XP direct access to IOs is not possible for
user applications (only kernel mode drivers). Because of that
a kernel driver is needed. The sources to GIVEIO.SYS are in
the respective directory. The loaddrv sources come from the
archive that is mentioned in the giveio readme.

If the extension detects that it is running on an NT based system
(NT, 2k, XP) it activates the giveio driver to gain access to the
IO ports. To make this work, the giveio driver must be installed.
this can be done with the loaddrv tool. The batchfiles
"install_giveio.bat" and "remove_giveio.bat" do whats needed to
install or uninstall.

Thanks go to
 Dale Roberts for the giveio driver and to 
 Paula Tomlinson for the loaddrv sources

chris <cliechti@gmx.net>
