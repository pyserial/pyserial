// Parallel port extension for Win32
// "inp" and "outp" are used to access the parallelport hardware
// needs giveio.sys driver on NT/2k/XP
//
// (C) 2005 Chris Liechti <cliechti@gmx.net>
// this is distributed under a free software license, see license.txt

#include <windows.h>
#include <conio.h>

#define DRIVERNAME      "\\\\.\\giveio"

/* module-functions */

WINAPI void outp(int port, int value) {
    _outp(port, value);
}

WINAPI int inp(int port) {
    int value;
    value = _inp(port);
    return value;
}

WINAPI int init(void) {
    OSVERSIONINFO vi;
    
    //detect OS, on NT,2k,XP the driver needs to be loaded
    vi.dwOSVersionInfoSize = sizeof(vi);
    GetVersionEx(&vi);
    if (vi.dwPlatformId == VER_PLATFORM_WIN32_NT) {
        HANDLE h;
        //try to open driver
        h = CreateFile(DRIVERNAME, GENERIC_READ, 0, NULL,
                       OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
        if (h == INVALID_HANDLE_VALUE) {
            //if it fails again, then we have a problem... -> exception
            //"Couldn't access giveio device";
            return 1;
        }
        //close again immediately.
        //the process is now tagged to have the rights it needs,
        //the giveio driver remembers that
        if (h != NULL) CloseHandle(h);          //close the driver's file
    }
    return 0;
}
