// Parallel port extension for Win32
// "inp" and "outp" are used to access the parallelport hardware
// needs giveio.sys driver on NT/2k/XP
//
// (C) 2002 Chris Liechti <cliechti@gmx.net>
// this is distributed under a free software license, see license.txt

#include <Python.h>
#include <windows.h>
#include <conio.h>

#define DRIVERNAME      "\\\\.\\giveio"

/* module-functions */

static PyObject*
py_outp(PyObject *self, PyObject *args)
{
    int port, value;
    if(!PyArg_ParseTuple(args, "ii", &port, &value))
        return 0;
    _outp(port, value);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
py_inp(PyObject *self, PyObject *args)
{
    int port, value;
    if(!PyArg_ParseTuple(args, "i", &port))
        return 0;
    value = _inp(port);
    return Py_BuildValue("i", value);
}



static PyMethodDef pypar_methods[] = {
    {"outp",   py_outp,   METH_VARARGS},
    {"inp",    py_inp,    METH_VARARGS},
    {0, 0}
};

/* module entry-point (module-initialization) function */
void init_pyparallel(void) {
    OSVERSIONINFO vi;
    
    /* Create the module and add the functions */
    Py_InitModule("_pyparallel", pypar_methods);
    
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
            PyErr_Format(PyExc_ImportError, "Couldn't access giveio device");
        }
        //close again immediately.
        //the process is now tagged to have the rights it needs,
        //the giveio driver remembers that
        if (h != NULL) CloseHandle(h);          //close the driver's file
    }
}
