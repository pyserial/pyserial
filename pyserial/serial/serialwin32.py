#! python
#serial driver for win32
#see __init__.py
#
#(C) 2001-2002 Chris Liechti <cliechti@gmx.net>
# this is distributed under a free software license, see license.txt

import win32file  # The base COM port and file IO functions.
import win32event # We use events and the WaitFor[Single|Multiple]Objects functions.
import win32con   # constants.
import sys, string
import serialutil

VERSION = string.split("$Revision: 1.23 $")[1]     #extract CVS version

PARITY_NONE, PARITY_EVEN, PARITY_ODD = range(3)
STOPBITS_ONE, STOPBITS_TWO = (1, 2)
FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS = (5,6,7,8)

portNotOpenError = ValueError('port not open')

#from winbase.h. these should realy be in win32con
MS_CTS_ON  = 16
MS_DSR_ON  = 32
MS_RING_ON = 64
MS_RLSD_ON = 128

def device(portnum):
    #the "//./COMx" format is required for devices > 9
    #not all versions of windows seem to support this propperly
    #so that the first few ports are used with the DOS device name
    if portnum < 9:
        return 'COM%d' % (portnum+1) #numbers are transformed to a string
    else:
        return r'\\.\COM%d' % (portnum+1)

class Serial(serialutil.FileLike):
    def __init__(self,
                 port,                  #number of device, numbering starts at
                                        #zero. if everything fails, the user
                                        #can specify a device string, note
                                        #that this isn't portable anymore
                 baudrate=9600,         #baudrate
                 bytesize=EIGHTBITS,    #number of databits
                 parity=PARITY_NONE,    #enable parity checking
                 stopbits=STOPBITS_ONE, #number of stopbits
                 timeout=None,          #set a timeout value, None to wait forever
                 xonxoff=0,             #enable software flow control
                 rtscts=0,              #enable RTS/CTS flow control
                 ):
        """initialize comm port"""

        self.timeout = timeout

        if type(port) == type(''):       #strings are taken directly
            self.portstr = port
        else:
            self.portstr = device(port)

        try:
            self.hComPort = win32file.CreateFile(self.portstr,
                   win32con.GENERIC_READ | win32con.GENERIC_WRITE,
                   0, # exclusive access
                   None, # no security
                   win32con.OPEN_EXISTING,
                   win32con.FILE_ATTRIBUTE_NORMAL | win32con.FILE_FLAG_OVERLAPPED,
                   None)
        except Exception, msg:
            self.hComPort = None    #'cause __del__ is called anyway
            raise serialutil.SerialException, "could not open port: %s" % msg
        # Setup a 4k buffer
        win32file.SetupComm(self.hComPort, 4096, 4096)

        #Save original timeout values:
        self.orgTimeouts = win32file.GetCommTimeouts(self.hComPort)

        #Set Windows timeout values
        #timeouts is a tuple with the following items:
        #(ReadIntervalTimeout,ReadTotalTimeoutMultiplier,
        # ReadTotalTimeoutConstant,WriteTotalTimeoutMultiplier,
        # WriteTotalTimeoutConstant)
        if timeout is None:
            timeouts = (0, 0, 0, 0, 0)
        elif timeout == 0:
            timeouts = (win32con.MAXDWORD, 0, 0, 0, 0)
        else:
            #timeouts = (0, 0, 0, 0, 0) #timeouts are done with WaitForSingleObject
            timeouts = (0, 0, int(timeout*1000), 0, 0)
        win32file.SetCommTimeouts(self.hComPort, timeouts)

        #win32file.SetCommMask(self.hComPort, win32file.EV_RXCHAR | win32file.EV_TXEMPTY |
        #    win32file.EV_RXFLAG | win32file.EV_ERR)
        #~ win32file.SetCommMask(self.hComPort,
                #~ win32file.EV_RXCHAR | win32file.EV_RXFLAG | win32file.EV_ERR)
        win32file.SetCommMask(self.hComPort, win32file.EV_ERR)

        # Setup the connection info.
        # Get state and modify it:
        comDCB = win32file.GetCommState(self.hComPort)
        comDCB.BaudRate = baudrate

        if bytesize == FIVEBITS:
            comDCB.ByteSize     = 5
        elif bytesize == SIXBITS:
            comDCB.ByteSize     = 6
        elif bytesize == SEVENBITS:
            comDCB.ByteSize     = 7
        elif bytesize == EIGHTBITS:
            comDCB.ByteSize     = 8

        if parity == PARITY_NONE:
            comDCB.Parity       = win32file.NOPARITY
            comDCB.fParity      = 0 # Dis/Enable Parity Check
        elif parity == PARITY_EVEN:
            comDCB.Parity       = win32file.EVENPARITY
            comDCB.fParity      = 1 # Dis/Enable Parity Check
        elif parity == PARITY_ODD:
            comDCB.Parity       = win32file.ODDPARITY
            comDCB.fParity      = 1 # Dis/Enable Parity Check

        if stopbits == STOPBITS_ONE:
            comDCB.StopBits     = win32file.ONESTOPBIT
        elif stopbits == STOPBITS_TWO:
            comDCB.StopBits     = win32file.TWOSTOPBITS
        comDCB.fBinary          = 1 # Enable Binary Transmission
        # Char. w/ Parity-Err are replaced with 0xff (if fErrorChar is set to TRUE)
        if rtscts:
            comDCB.fRtsControl  = win32file.RTS_CONTROL_HANDSHAKE
            comDCB.fDtrControl  = win32file.DTR_CONTROL_HANDSHAKE
        else:
            comDCB.fRtsControl  = win32file.RTS_CONTROL_ENABLE
            comDCB.fDtrControl  = win32file.DTR_CONTROL_ENABLE
        comDCB.fOutxCtsFlow     = rtscts
        comDCB.fOutxDsrFlow     = rtscts
        comDCB.fOutX            = xonxoff
        comDCB.fInX             = xonxoff
        comDCB.fNull            = 0
        comDCB.fErrorChar       = 0
        comDCB.fAbortOnError    = 0

        win32file.SetCommState(self.hComPort, comDCB)

        # Clear buffers:
        # Remove anything that was there
        win32file.PurgeComm(self.hComPort,
                            win32file.PURGE_TXCLEAR | win32file.PURGE_TXABORT |
                            win32file.PURGE_RXCLEAR | win32file.PURGE_RXABORT)

        #print win32file.ClearCommError(self.hComPort) #flags, comState =

        self._overlappedRead = win32file.OVERLAPPED()
        self._overlappedRead.hEvent = win32event.CreateEvent(None, 1, 0, None)
        self._overlappedWrite = win32file.OVERLAPPED()
        self._overlappedWrite.hEvent = win32event.CreateEvent(None, 0, 0, None)

    def __del__(self):
        self.close()

    def close(self):
        """close port"""
        if self.hComPort:
            #Restore original timeout values:
            win32file.SetCommTimeouts(self.hComPort, self.orgTimeouts)
            #Close COM-Port:
            win32file.CloseHandle(self.hComPort)
            self.hComPort = None

    def setBaudrate(self, baudrate):
        """change baudrate after port is open"""
        if not self.hComPort: raise portNotOpenError
        # Setup the connection info.
        # Get state and modify it:
        comDCB = win32file.GetCommState(self.hComPort)
        comDCB.BaudRate = baudrate
        win32file.SetCommState(self.hComPort, comDCB)

    def inWaiting(self):
        """returns the number of bytes waiting to be read"""
        flags, comstat = win32file.ClearCommError(self.hComPort)
        return comstat.cbInQue

    def read(self, size=1):
        """read num bytes from serial port"""
        if not self.hComPort: raise portNotOpenError
        if size > 0:
            win32event.ResetEvent(self._overlappedRead.hEvent)
            flags, comstat = win32file.ClearCommError(self.hComPort)
            if self.timeout == 0:
                n = min(comstat.cbInQue, size)
                if n > 0:
                    rc, buf = win32file.ReadFile(self.hComPort, win32file.AllocateReadBuffer(n), self._overlappedRead)
                    win32event.WaitForSingleObject(self._overlappedRead.hEvent, win32event.INFINITE)
                    read = str(buf)
                else:
                    read = ''
            else:
                rc, buf = win32file.ReadFile(self.hComPort, win32file.AllocateReadBuffer(size), self._overlappedRead)
                n = win32file.GetOverlappedResult(self.hComPort, self._overlappedRead, 1)
                read = str(buf[:n])
        else:
            read = ''
        return read

    def write(self, s):
        """write string to serial port"""
        if not self.hComPort: raise portNotOpenError
        #print repr(s),
        if s:
            err, n = win32file.WriteFile(self.hComPort, s, self._overlappedWrite)
            if err: #will be ERROR_IO_PENDING:
                # Wait for the write to complete.
                win32event.WaitForSingleObject(self._overlappedWrite.hEvent, win32event.INFINITE)

    def flushInput(self):
        if not self.hComPort: raise portNotOpenError
        win32file.PurgeComm(self.hComPort, win32file.PURGE_RXCLEAR | win32file.PURGE_RXABORT)

    def flushOutput(self):
        if not self.hComPort: raise portNotOpenError
        win32file.PurgeComm(self.hComPort, win32file.PURGE_TXCLEAR | win32file.PURGE_TXABORT)

    def sendBreak(self):
        if not self.hComPort: raise portNotOpenError
        import time
        win32file.SetCommBreak(self.hComPort)
        #TODO: how to set the correct duration??
        time.sleep(0.020)
        win32file.ClearCommBreak(self.hComPort)

    def setRTS(self,level=1):
        """set terminal status line"""
        if not self.hComPort: raise portNotOpenError
        if level:
            win32file.EscapeCommFunction(self.hComPort, win32file.SETRTS)
        else:
            win32file.EscapeCommFunction(self.hComPort, win32file.CLRRTS)

    def setDTR(self,level=1):
        """set terminal status line"""
        if not self.hComPort: raise portNotOpenError
        if level:
            win32file.EscapeCommFunction(self.hComPort, win32file.SETDTR)
        else:
            win32file.EscapeCommFunction(self.hComPort, win32file.CLRDTR)

    def getCTS(self):
        """read terminal status line"""
        if not self.hComPort: raise portNotOpenError
        return MS_CTS_ON & win32file.GetCommModemStatus(self.hComPort) != 0

    def getDSR(self):
        """read terminal status line"""
        if not self.hComPort: raise portNotOpenError
        return MS_DSR_ON & win32file.GetCommModemStatus(self.hComPort) != 0

    def getRI(self):
        """read terminal status line"""
        if not self.hComPort: raise portNotOpenError
        return MS_RING_ON & win32file.GetCommModemStatus(self.hComPort) != 0

    def getCD(self):
        """read terminal status line"""
        if not self.hComPort: raise portNotOpenError
        return MS_RLSD_ON & win32file.GetCommModemStatus(self.hComPort) != 0

#Nur Testfunktion!!
if __name__ == '__main__':
    print __name__
    s = Serial(0)

