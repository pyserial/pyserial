#! python
#
# async backend for Windows ("win32" incl. 32/64 bit support)
#
# (C) 2001-2020 Chris Liechti <cliechti@gmx.net>
#
# This file is part of pySerial. https://github.com/pyserial/pyserial
# SPDX-License-Identifier:    BSD-3-Clause
#
# Initial patch to use ctypes by Giovanni Bajo <rasky@develer.com>

import asyncio

# pylint: disable=invalid-name,too-few-public-methods
import ctypes
from functools import reduce
from typing import Optional
from serial import win32

import serial
from serial.serialutil import SerialBase, SerialException, to_bytes, PortNotOpenError, SerialTimeoutException


class AsyncSerial(SerialBase):
    """Async serial port implementation for Win32 based on ctypes."""

    BAUDRATES = (50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800,
                 9600, 19200, 38400, 57600, 115200)
    
    _WIN32_EVENT_SECURITY_ATTR = None
    _WIN32_EVENT_MANUAL_RESET = True
    _WIN32_EVENT_INITIAL_STATE = False
    _WIN32_EVENT_NAME = None

    _BUFFER_SIZE = 4096

    _SET_COMM_MASKS = (
        win32.EV_BREAK,
        win32.EV_CTS,
        win32.EV_DSR,
        win32.EV_ERR,
        win32.EV_RXCHAR,
        win32.EV_TXEMPTY
    )

    _SET_COMM_MASK = reduce(lambda acc, x: acc | x, _SET_COMM_MASKS)

    def __init__(self, *args, loop: Optional[asyncio.ProactorEventLoop] = None, **kwargs):
        loop = loop or asyncio.get_running_loop()
        if type(loop) != asyncio.windows_events.ProactorEventLoop:
            raise NotImplementedError("Only implemented for the ProactorEventLoop!")

        self._loop = loop

        super().__init__(*args, **kwargs)

    def open(self):
        """\
        Open port with current settings. This may throw a SerialException
        if the port cannot be opened.
        """
        if self._port is None:
            raise SerialException("Port must be configured before it can be used.")
        if self.is_open:
            raise SerialException("Port is already open.")
        # the "\\.\COMx" format is required for devices other than COM1-COM8
        # not all versions of windows seem to support this properly
        # so that the first few ports are used with the DOS device name
        port = self.name
        try:
            if port.upper().startswith('COM') and int(port[3:]) > 8:
                port = '\\\\.\\' + port
        except ValueError:
            # for like COMnotanumber
            pass
        self._port_handle = win32.CreateFile(
            port,
            win32.GENERIC_READ | win32.GENERIC_WRITE,
            0,  # exclusive access
            None,  # no security
            win32.OPEN_EXISTING,
            win32.FILE_ATTRIBUTE_NORMAL | win32.FILE_FLAG_OVERLAPPED,
            0
        )
        if self._port_handle == win32.INVALID_HANDLE_VALUE:
            self._port_handle = None    # 'cause __del__ is called anyway
            raise SerialException("could not open port {!r}: {!r}".format(self.portstr, ctypes.WinError()))

        try:
            self._overlapped_read = win32.OVERLAPPED()
            self._overlapped_read.hEvent = win32.CreateEvent(
                self._WIN32_EVENT_SECURITY_ATTR,
                self._WIN32_EVENT_MANUAL_RESET,
                self._WIN32_EVENT_INITIAL_STATE,
                self._WIN32_EVENT_NAME
            )

            self._overlapped_write = win32.OVERLAPPED()
            self._overlapped_write.hEvent = win32.CreateEvent(
                self._WIN32_EVENT_SECURITY_ATTR,
                self._WIN32_EVENT_MANUAL_RESET,
                self._WIN32_EVENT_INITIAL_STATE,
                self._WIN32_EVENT_NAME
            )

            win32.SetupComm(self._port_handle, self._BUFFER_SIZE, self._BUFFER_SIZE)

            # Save original timeout values:
            self._original_timeouts = win32.COMMTIMEOUTS()
            win32.GetCommTimeouts(self._port_handle, ctypes.byref(self._original_timeouts))

            self._reconfigure_port()

            # Clear buffers:
            win32.PurgeComm(
                self._port_handle,
                win32.PURGE_TXCLEAR | win32.PURGE_TXABORT |
                win32.PURGE_RXCLEAR | win32.PURGE_RXABORT
            )

        except:
            try:
                self._close()
            except:
                # ignore any exception when closing the port
                # also to keep original exception that happened when setting up
                pass
            self._port_handle = None
            raise
        else:
            self.is_open = True
        
        self._read_future = self._loop._proactor.wait_for_handle(self._overlapped_read.hEvent)
        self._write_future = self._loop._proactor.wait_for_handle(self._overlapped_write.hEvent)

        self._wait_for_reads_task = asyncio.create_task(self._make_wait_for_event("read"))
        self._wait_for_writes_task = asyncio.create_task(self._make_wait_for_event("write"))
        
        self._read_lock = asyncio.Lock()
        self._write_lock = asyncio.Lock()

    def _reconfigure_port(self):
        """Set communication parameters on opened port."""
        if not self._port_handle:
            raise SerialException("Can only operate on a valid port handle")

        timeouts = win32.COMMTIMEOUTS()
        timeouts.ReadIntervalTimeout = self._inter_byte_timeout * 1000 if self._inter_byte_timeout else 0
        timeouts.ReadTotalTimeoutConstant = self._timeout * 1000 if self._timeout else 0
        timeouts.ReadTotalTimeoutMultiplier = 0

        if self._write_timeout is None:
            pass
        elif self._write_timeout == 0:
            timeouts.WriteTotalTimeoutConstant = win32.MAXDWORD
        else:
            timeouts.WriteTotalTimeoutConstant = max(int(self._write_timeout * 1000), 1)
        win32.SetCommTimeouts(self._port_handle, ctypes.byref(timeouts))

        win32.SetCommMask(self._port_handle, self._SET_COMM_MASK)

        # Setup the connection info.
        # Get state and modify it:
        comDCB = win32.DCB()
        win32.GetCommState(self._port_handle, ctypes.byref(comDCB))
        comDCB.BaudRate = self._baudrate

        if self._bytesize == serial.FIVEBITS:
            comDCB.ByteSize = 5
        elif self._bytesize == serial.SIXBITS:
            comDCB.ByteSize = 6
        elif self._bytesize == serial.SEVENBITS:
            comDCB.ByteSize = 7
        elif self._bytesize == serial.EIGHTBITS:
            comDCB.ByteSize = 8
        else:
            raise ValueError("Unsupported number of data bits: {!r}".format(self._bytesize))

        if self._parity == serial.PARITY_NONE:
            comDCB.Parity = win32.NOPARITY
            comDCB.fParity = 0  # Disable Parity Check
        elif self._parity == serial.PARITY_EVEN:
            comDCB.Parity = win32.EVENPARITY
            comDCB.fParity = 1  # Enable Parity Check
        elif self._parity == serial.PARITY_ODD:
            comDCB.Parity = win32.ODDPARITY
            comDCB.fParity = 1  # Enable Parity Check
        elif self._parity == serial.PARITY_MARK:
            comDCB.Parity = win32.MARKPARITY
            comDCB.fParity = 1  # Enable Parity Check
        elif self._parity == serial.PARITY_SPACE:
            comDCB.Parity = win32.SPACEPARITY
            comDCB.fParity = 1  # Enable Parity Check
        else:
            raise ValueError("Unsupported parity mode: {!r}".format(self._parity))

        if self._stopbits == serial.STOPBITS_ONE:
            comDCB.StopBits = win32.ONESTOPBIT
        elif self._stopbits == serial.STOPBITS_ONE_POINT_FIVE:
            comDCB.StopBits = win32.ONE5STOPBITS
        elif self._stopbits == serial.STOPBITS_TWO:
            comDCB.StopBits = win32.TWOSTOPBITS
        else:
            raise ValueError("Unsupported number of stop bits: {!r}".format(self._stopbits))

        comDCB.fBinary = 1  # Enable Binary Transmission
        # Char. w/ Parity-Err are replaced with 0xff (if fErrorChar is set to TRUE)
        if self._rs485_mode is None:
            if self._rtscts:
                comDCB.fRtsControl = win32.RTS_CONTROL_HANDSHAKE
            else:
                comDCB.fRtsControl = win32.RTS_CONTROL_ENABLE if self._rts_state else win32.RTS_CONTROL_DISABLE
            comDCB.fOutxCtsFlow = self._rtscts
        else:
            # checks for unsupported settings
            # XXX verify if platform really does not have a setting for those
            if not self._rs485_mode.rts_level_for_tx:
                raise ValueError(
                    'Unsupported value for RS485Settings.rts_level_for_tx: {!r} (only True is allowed)'.format(
                        self._rs485_mode.rts_level_for_tx,))
            if self._rs485_mode.rts_level_for_rx:
                raise ValueError(
                    'Unsupported value for RS485Settings.rts_level_for_rx: {!r} (only False is allowed)'.format(
                        self._rs485_mode.rts_level_for_rx,))
            if self._rs485_mode.delay_before_tx is not None:
                raise ValueError(
                    'Unsupported value for RS485Settings.delay_before_tx: {!r} (only None is allowed)'.format(
                        self._rs485_mode.delay_before_tx,))
            if self._rs485_mode.delay_before_rx is not None:
                raise ValueError(
                    'Unsupported value for RS485Settings.delay_before_rx: {!r} (only None is allowed)'.format(
                        self._rs485_mode.delay_before_rx,))
            if self._rs485_mode.loopback:
                raise ValueError(
                    'Unsupported value for RS485Settings.loopback: {!r} (only False is allowed)'.format(
                        self._rs485_mode.loopback,))
            comDCB.fRtsControl = win32.RTS_CONTROL_TOGGLE
            comDCB.fOutxCtsFlow = 0

        if self._dsrdtr:
            comDCB.fDtrControl = win32.DTR_CONTROL_HANDSHAKE
        else:
            comDCB.fDtrControl = win32.DTR_CONTROL_ENABLE if self._dtr_state else win32.DTR_CONTROL_DISABLE
        comDCB.fOutxDsrFlow = self._dsrdtr
        comDCB.fOutX = self._xonxoff
        comDCB.fInX = self._xonxoff
        comDCB.fNull = 0
        comDCB.fErrorChar = 0
        comDCB.fAbortOnError = 0
        comDCB.XonChar = serial.XON
        comDCB.XoffChar = serial.XOFF

        if not win32.SetCommState(self._port_handle, ctypes.byref(comDCB)):
            raise SerialException(
                'Cannot configure port, something went wrong. '
                'Original message: {!r}'.format(ctypes.WinError()))


    def close(self):
        """Close port"""
        if not self.is_open:
            return
        
        if self._port_handle is not None:
            # Restore original timeout values:
            win32.SetCommTimeouts(self._port_handle, self._original_timeouts)
        if self._overlapped_read is not None:
            self.cancel_read()
            win32.CloseHandle(self._overlapped_read.hEvent)
            self._overlapped_read = None
        if self._overlapped_write is not None:
            self.cancel_write()
            win32.CloseHandle(self._overlapped_write.hEvent)
            self._overlapped_write = None
        win32.CloseHandle(self._port_handle)
        self._port_handle = None
        self.is_open = False

    @property
    def in_waiting(self):
        """Return the number of bytes currently in the input buffer."""
        flags = win32.DWORD()
        comstat = win32.COMSTAT()
        if not win32.ClearCommError(self._port_handle, ctypes.byref(flags), ctypes.byref(comstat)):
            raise SerialException("ClearCommError failed ({!r})".format(ctypes.WinError()))
        return comstat.cbInQue

    async def read(self, size=1):
        """\
        Read size bytes from the serial port. If a timeout is set it may
        return less characters as requested. With no timeout it will block
        until the requested number of bytes is read.
        """
        
        if not self.is_open:
            raise PortNotOpenError()

        if size < 1:
            return bytes()

        async with self._read_lock:
            
            # create the event that will resolve on write completion
            self._read_complete_event = self.CommEvent(self._overlapped_read, win32.EV_RXCHAR)
            
            read_buffer = ctypes.create_string_buffer(size)

            win32.ReadFile(
                self._port_handle,
                read_buffer,
                size,
                None,
                self._overlapped_read
            )

            await self._read_complete_event.wait()

            if self._read_complete_event.exception:
                raise self._read_complete_event.exception

            return read_buffer.raw[:self._read_complete_event.bytes_transferred]
        
    
    async def write(self, data):
        """Output the given byte string over the serial port."""
        if not self.is_open:
            raise PortNotOpenError()
        
        data = to_bytes(data)

        if not data:
            return 0

        async with self._write_lock:

            # create the event that will resolve on write completion
            self._write_complete_event = self.CommEvent(self._overlapped_write, win32.EV_TXEMPTY)
            
            win32.WriteFile(self._port_handle, data, len(data), None, self._overlapped_write)
            await self._write_complete_event.wait()

            if self._write_complete_event.exception:
                raise self._write_complete_event.exception
            
            if (self._write_complete_event.bytes_transferred < len(data)):
                raise SerialTimeoutException(f"{self._write_complete_event.bytes_transferred} of {len(data)} bytes written.")

            return self._write_complete_event.bytes_transferred

    
    class CommEvent(asyncio.Event):
        def __init__(self, overlapped: win32.OVERLAPPED, comm_mask: int):
            self._overlapped = overlapped
            self._comm_mask = comm_mask

            self.exception: Optional[Exception] = None
            self.bytes_transferred = 0

            super().__init__()
        
        @property
        def overlapped(self):
            return self._overlapped
        
        @property
        def comm_mask(self):
            return self._comm_mask


    def _make_wait_for_event(self, read_or_write: str,):

        future = f"_{read_or_write}_future"
        event = f"_{read_or_write}_complete_event"

        async def wait_loop(event):
            EvtMask = win32.DWORD(0)
            NumberOfBytesTransferred = win32.DWORD(0)
            Errors = win32.DWORD(0)
            Comstat = win32.COMSTAT()
           
            while True:
                await getattr(self, future)

                event = getattr(self, event)

                event.bytes_transferred = event.overlapped.InternalHigh
                event.exception = None

                # get the event
                event_success = win32.WaitCommEvent(
                    self._port_handle,
                    ctypes.byref(EvtMask),
                    ctypes.byref(event.overlapped)
                )

                if not event_success:
                    # check for errors
                    success = win32.GetOverlappedResult(
                        self._port_handle,
                        event.overlapped,
                        ctypes.byref(NumberOfBytesTransferred),
                        False
                    )

                    if not success: 
                        error = win32.GetLastError()
                        if error not in {win32.ERROR_IO_PENDING, win32.ERROR_SUCCESS}:
                            self._cancel_overlapped_io(event.overlapped)
                        if error not in {win32.ERROR_IO_PENDING, win32.ERROR_SUCCESS, win32.ERROR_IO_INCOMPLETE}:
                            event.exception = SerialException(f"Error: {error}")
                
                # reset and create the new future
                win32.ResetEvent(event.overlapped.hEvent)
                setattr(self, future, self._loop._proactor.wait_for_handle(event.overlapped.hEvent))

                # check the state of the buffer
                if not win32.ClearCommError(self._port_handle, ctypes.byref(Errors), ctypes.byref(Comstat)):
                    raise SerialException("ClearCommError failed ({!r})".format(ctypes.WinError()))
                bytes_in_buffer = Comstat.cbInQue if read_or_write == "read" else Comstat.dbOutQue
                if bytes_in_buffer > 0:
                    # if there are bytes in the buffer they may have come in while handling the signal
                    win32.SetEvent(event.overlapped.hEvent)

                # handle event

                if (EvtMask.value & win32.EV_ERR == win32.EV_ERR):
                    raise SerialException("Error in WaitCommEvent!")

                elif EvtMask.value == 0 or EvtMask.value & event.comm_mask:
                    event.set()
            
        return wait_loop(event)
                    

    def flush(self):
        """\
        Flush of file like objects. In this case, wait until all data
        is written.
        """
        if self.out_waiting == 0:
            return

        EvtMask = win32.DWORD(0)
        while (EvtMask.value & win32.EV_TXEMPTY) != win32.EV_TXEMPTY:
            win32.WaitCommEvent(
                self._port_handle,
                ctypes.byref(EvtMask),
                ctypes.byref(self._overlapped_write)
            )

    def reset_input_buffer(self):
        """Clear input buffer, discarding all that is in the buffer."""
        if not self.is_open:
            raise PortNotOpenError()
        win32.PurgeComm(self._port_handle, win32.PURGE_RXCLEAR | win32.PURGE_RXABORT)

    def reset_output_buffer(self):
        """\
        Clear output buffer, aborting the current output and discarding all
        that is in the buffer.
        """
        if not self.is_open:
            raise PortNotOpenError()
        win32.PurgeComm(self._port_handle, win32.PURGE_TXCLEAR | win32.PURGE_TXABORT)

    def _update_break_state(self):
        """Set break: Controls TXD. When active, to transmitting is possible."""
        if not self.is_open:
            raise PortNotOpenError()
        if self._break_state:
            win32.SetCommBreak(self._port_handle)
        else:
            win32.ClearCommBreak(self._port_handle)

    def _update_rts_state(self):
        """Set terminal status line: Request To Send"""
        if self._rts_state:
            win32.EscapeCommFunction(self._port_handle, win32.SETRTS)
        else:
            win32.EscapeCommFunction(self._port_handle, win32.CLRRTS)

    def _update_dtr_state(self):
        """Set terminal status line: Data Terminal Ready"""
        if self._dtr_state:
            win32.EscapeCommFunction(self._port_handle, win32.SETDTR)
        else:
            win32.EscapeCommFunction(self._port_handle, win32.CLRDTR)

    def _GetCommModemStatus(self):
        if not self.is_open:
            raise PortNotOpenError()
        stat = win32.DWORD()
        win32.GetCommModemStatus(self._port_handle, ctypes.byref(stat))
        return stat.value

    @property
    def cts(self):
        """Read terminal status line: Clear To Send"""
        return win32.MS_CTS_ON & self._GetCommModemStatus() != 0

    @property
    def dsr(self):
        """Read terminal status line: Data Set Ready"""
        return win32.MS_DSR_ON & self._GetCommModemStatus() != 0

    @property
    def ri(self):
        """Read terminal status line: Ring Indicator"""
        return win32.MS_RING_ON & self._GetCommModemStatus() != 0

    @property
    def cd(self):
        """Read terminal status line: Carrier Detect"""
        return win32.MS_RLSD_ON & self._GetCommModemStatus() != 0

    # - - platform specific - - - -

    def set_buffer_size(self, rx_size=4096, tx_size=None):
        """\
        Recommend a buffer size to the driver (device driver can ignore this
        value). Must be called after the port is opened.
        """
        if tx_size is None:
            tx_size = rx_size
        win32.SetupComm(self._port_handle, rx_size, tx_size)

    def set_output_flow_control(self, enable=True):
        """\
        Manually control flow - when software flow control is enabled.
        This will do the same as if XON (true) or XOFF (false) are received
        from the other device and control the transmission accordingly.
        WARNING: this function is not portable to different platforms!
        """
        if not self.is_open:
            raise PortNotOpenError()
        if enable:
            win32.EscapeCommFunction(self._port_handle, win32.SETXON)
        else:
            win32.EscapeCommFunction(self._port_handle, win32.SETXOFF)

    @property
    def out_waiting(self):
        """Return how many bytes the in the outgoing buffer"""
        flags = win32.DWORD()
        comstat = win32.COMSTAT()
        if not win32.ClearCommError(self._port_handle, ctypes.byref(flags), ctypes.byref(comstat)):
            raise SerialException("ClearCommError failed ({!r})".format(ctypes.WinError()))
        return comstat.cbOutQue

    def _cancel_overlapped_io(self, overlapped):
        """Cancel a blocking read operation, may be called from other thread"""
        # check if read operation is pending
        rc = win32.DWORD()
        err = win32.GetOverlappedResult(
            self._port_handle,
            ctypes.byref(overlapped),
            ctypes.byref(rc),
            False)
        if not err and win32.GetLastError() in (win32.ERROR_IO_PENDING, win32.ERROR_IO_INCOMPLETE):
            # cancel, ignoring any errors (e.g. it may just have finished on its own)
            win32.CancelIoEx(self._port_handle, overlapped)

    def cancel_read(self):
        """Cancel a blocking read operation, may be called from other thread"""
        self._cancel_overlapped_io(self._overlapped_read)

    def cancel_write(self):
        """Cancel a blocking write operation, may be called from other thread"""
        self._cancel_overlapped_io(self._overlapped_write)

    @SerialBase.exclusive.setter
    def exclusive(self, exclusive):
        """Change the exclusive access setting."""
        if exclusive is not None and not exclusive:
            raise ValueError('win32 only supports exclusive access (not: {})'.format(exclusive))
        else:
            serial.SerialBase.exclusive.__set__(self, exclusive)
