// loaddrv.c - Dynamic driver install/start/stop/remove
// original by Paula Tomlinson

#include <windows.h>
#include "loaddrv.h"

SC_HANDLE hSCMan = NULL;

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

DWORD DriverInstall(LPSTR lpPath, LPSTR lpDriver) {
   BOOL dwStatus = OKAY;
   SC_HANDLE hService = NULL;

   // add to service control manager's database
   if ((hService = CreateService(hSCMan, lpDriver, 
      lpDriver, SERVICE_ALL_ACCESS, SERVICE_KERNEL_DRIVER,
      SERVICE_DEMAND_START, SERVICE_ERROR_NORMAL, lpPath, 
      NULL, NULL, NULL, NULL, NULL)) == NULL) 
   {
         dwStatus = GetLastError();
   } else {
       CloseServiceHandle(hService);
   }

   return dwStatus;
}

DWORD DriverStart(LPSTR lpDriver) {
   BOOL dwStatus = OKAY;
   SC_HANDLE hService = NULL;

   // get a handle to the service
   if ((hService = OpenService(hSCMan, lpDriver, 
      SERVICE_ALL_ACCESS)) != NULL) 
   {
      // start the driver
      if (!StartService(hService, 0, NULL))
         dwStatus = GetLastError();
   } else {
       dwStatus = GetLastError();
   }

   if (hService != NULL) {
       CloseServiceHandle(hService);
   }
   return dwStatus;
}

DWORD DriverStop(LPSTR lpDriver) {
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
   } else {
       dwStatus = GetLastError();
   }

   if (hService != NULL) {
       CloseServiceHandle(hService);
   }
   return dwStatus;
}

DWORD DriverRemove(LPSTR lpDriver) {
   BOOL dwStatus = OKAY;
   SC_HANDLE hService = NULL;

   // get a handle to the service
   if ((hService = OpenService(hSCMan, lpDriver, 
      SERVICE_ALL_ACCESS)) != NULL) 
   {
      // remove the driver
      if (!DeleteService(hService))
         dwStatus = GetLastError();
   } else {
       dwStatus = GetLastError();
   }

   if (hService != NULL) {
       CloseServiceHandle(hService);
   }
   return dwStatus;
}
