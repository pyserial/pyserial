This extension is needed on Windows as there is no API to
manipulate the parallel port. This Python extension exposes
"inp()" and "outp()" that can be used to manipulate the printer
IOs directly. It could be basicaly used to access any IO port.

On Windows NT/2k/XP direct access to IOs is not possible for
user applications (only kernel mode drivers). Because of that
a kernel driver is needed. The sources to GIVEIO.SYS are in
the respective directory. The loaddrv sources come from the
archive that is mentioned in the giveio readme.

The extension tries to detect if its running on an NT based
system and activates the giveio driver to gain access to the
IO ports.

Thanks go to
 Dale Roberts for the giveio driver and to 
 Paula Tomlinson for the loaddrv sources

chris <cliechti@gmx.net>
