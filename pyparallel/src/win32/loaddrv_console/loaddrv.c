// loaddrv.c - Dynamic driver install/start/stop/remove
// based on Paula Tomlinson's LOADDRV program. 
// She describes it in her May 1995 article in Windows/DOS Developer's
// Journal (now Windows Developer's Journal).
// i removed the old/ugly dialog, it now accepts command line options and
// prints error messages with textual description from the OS.

#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "loaddrv.h"

// globals
SC_HANDLE hSCMan = NULL;

//get ext messages for windows error codes:
void DisplayErrorText(DWORD dwLastError) {
    LPSTR MessageBuffer;
    DWORD dwBufferLength;
    
    DWORD dwFormatFlags = FORMAT_MESSAGE_ALLOCATE_BUFFER |
        FORMAT_MESSAGE_IGNORE_INSERTS |
        FORMAT_MESSAGE_FROM_SYSTEM;
    
    dwBufferLength = FormatMessageA(
        dwFormatFlags,
        NULL, // module to get message from (NULL == system)
        dwLastError,
        MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), // default language
        (LPSTR) &MessageBuffer,
        0,
        NULL
    );
    if (dwBufferLength) {
        // Output message
        puts(MessageBuffer);
        // Free the buffer allocated by the system.
        LocalFree(MessageBuffer);
    }
}

int exists(char *filename) {
    FILE * pFile;
    pFile = fopen(filename, "r");
    return pFile != NULL;
}

int main(int argc, char *argv[]) {
    DWORD status = 0;
    int level = 0;
    if (argc < 3) {
        printf("USGAE: loaddrv start|stop|install|remove drivername [fullpathforinstall]");
        exit(1);
    }
    LoadDriverInit();
    if (strcmp(argv[1], "start") == 0) {
        printf("starting %s... ", argv[2]);
        status = DriverStart(argv[2]);
        if ( status != OKAY) {
            printf("start failed (status %ld):\n", status);
            level = 1;
        } else {
            printf("ok.\n");
        }
    } else if (strcmp(argv[1], "stop") == 0) {
        printf("stoping %s... ", argv[2]);
        status = DriverStop(argv[2]);
        if ( status != OKAY) {
            printf("stop failed (status %ld):\n", status);
            level = 1;
        } else {
            printf("ok.\n");
        }
    } else if (strcmp(argv[1], "install") == 0) {
        char path[MAX_PATH*2];
        if (argc<4) {
            char cwd[MAX_PATH];
            getcwd(cwd, sizeof cwd);
            sprintf(path, "%s\\%s.sys", cwd, argv[2]);
        } else {
            strncpy(path, argv[3], MAX_PATH);
        }
        if (exists(path)) {
            printf("installing %s from %s... ", argv[2], path);
            status = DriverInstall(path, argv[2]);
            if ( status != OKAY) {
                printf("install failed (status %ld):\n", status);
                level = 2;
            } else {
                printf("ok.\n");
            }
        } else {
            printf("install failed, file not found: %s\n", path);
            level = 1;
        }
    } else if (strcmp(argv[1], "remove") == 0) {
        printf("removing %s... ", argv[2]);
        status = DriverRemove(argv[2]);
        if ( status != OKAY) {
            printf("remove failed (status %ld):\n", status);
            level = 1;
        } else {
            printf("ok.\n");
        }
    } else {
        printf("USGAE: loaddrv start|stop|install|remove drivername [fullpathforinstall]");
        level = 1;
    }
    if (status) DisplayErrorText(status);
    LoadDriverCleanup();
    exit(level);
    return 0;
}


DWORD LoadDriverInit(void) {
    // connect to local service control manager
    if ((hSCMan = OpenSCManager(NULL, NULL, 
        SC_MANAGER_ALL_ACCESS)) == NULL) {
        return -1;
    }
    return OKAY;
}

void LoadDriverCleanup(void) {
    if (hSCMan != NULL) CloseServiceHandle(hSCMan);
}

/**-----------------------------------------------------**/
DWORD DriverInstall(LPSTR lpPath, LPSTR lpDriver)
{
   BOOL dwStatus = OKAY;
   SC_HANDLE hService = NULL;

   // add to service control manager's database
   if ((hService = CreateService(hSCMan, lpDriver, 
      lpDriver, SERVICE_ALL_ACCESS, SERVICE_KERNEL_DRIVER,
      SERVICE_DEMAND_START, SERVICE_ERROR_NORMAL, lpPath, 
      NULL, NULL, NULL, NULL, NULL)) == NULL)
         dwStatus = GetLastError();
   else CloseServiceHandle(hService);

   return dwStatus;
} // DriverInstall

/**-----------------------------------------------------**/
DWORD DriverStart(LPSTR lpDriver)
{
   BOOL dwStatus = OKAY;
   SC_HANDLE hService = NULL;

   // get a handle to the service
   if ((hService = OpenService(hSCMan, lpDriver, 
      SERVICE_ALL_ACCESS)) != NULL) 
   {
      // start the driver
      if (!StartService(hService, 0, NULL))
         dwStatus = GetLastError();
   } else dwStatus = GetLastError();

   if (hService != NULL) CloseServiceHandle(hService);
   return dwStatus;
} // DriverStart

/**-----------------------------------------------------**/
DWORD DriverStop(LPSTR lpDriver)
{
   BOOL dwStatus = OKAY;
   SC_HANDLE hService = NULL;
   SERVICE_STATUS serviceStatus;

   // get a handle to the service
   if ((hService = OpenService(hSCMan, lpDriver, 
      SERVICE_ALL_ACCESS)) != NULL) 
   {
      // stop the driver
      if (!ControlService(hService, SERVICE_CONTROL_STOP,
         &serviceStatus))
            dwStatus = GetLastError();
   } else dwStatus = GetLastError();

   if (hService != NULL) CloseServiceHandle(hService);
   return dwStatus;
} // DriverStop

/**-----------------------------------------------------**/
DWORD DriverRemove(LPSTR lpDriver)
{
   BOOL dwStatus = OKAY;
   SC_HANDLE hService = NULL;

   // get a handle to the service
   if ((hService = OpenService(hSCMan, lpDriver, 
      SERVICE_ALL_ACCESS)) != NULL) 
   {
      // remove the driver
      if (!DeleteService(hService))
         dwStatus = GetLastError();
   } else dwStatus = GetLastError();

   if (hService != NULL) CloseServiceHandle(hService);
   return dwStatus;
} // DriverRemove
