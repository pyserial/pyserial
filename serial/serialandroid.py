import time
from serial.android import get_android_context
from com.hoho.android.usbserial.driver import UsbSerialProber, UsbSerialPort
from java.lang import UnsupportedOperationException
from serial.serialutil import SerialBase, SerialException, PortNotOpenError


class Serial(SerialBase):

    def open(self):
        if self._port is None:
            raise SerialException("Port must be configured before it can be used.")
        if self.is_open:
            raise SerialException("Port is already open.")
        context = get_android_context()
        usb_manager = context.getSystemService(context.USB_SERVICE)
        available_drivers = UsbSerialProber.getDefaultProber().findAllDrivers(usb_manager)
        if not available_drivers:
            raise SerialException("No USB serial device found.")

        self.driver = available_drivers.get(0)
        connection = usb_manager.openDevice(self.driver.getDevice())
        if connection is None:
            raise SerialException("Could not open connection to device.")
        self.fd = connection.getFileDescriptor()

        self.mik3yPort = self.driver.getPorts().get(0)
        self.mik3yPort.open(connection)
        self._reconfigure_port()
        self.is_open = True

    def _reconfigure_port(self):
        if not self.mik3yPort:
            raise SerialException("Can only operate on a valid port handle")

        # Map bytesize to UsbSerialPort constants
        if self._bytesize == 5:
            dataBits = UsbSerialPort.DATABITS_5
        elif self._bytesize == 6:
            dataBits = UsbSerialPort.DATABITS_6
        elif self._bytesize == 7:
            dataBits = UsbSerialPort.DATABITS_7
        elif self._bytesize == 8:
            dataBits = UsbSerialPort.DATABITS_8
        else:
            raise ValueError("unsupported bytesize: %r" % self._bytesize)

        # Map stopbits to UsbSerialPort constants
        if self._stopbits == 1:
            stopBits = UsbSerialPort.STOPBITS_1
        elif self._stopbits == 1.5:
            stopBits = UsbSerialPort.STOPBITS_1_5
        elif self._stopbits == 2:
            stopBits = UsbSerialPort.STOPBITS_2
        else:
            raise ValueError("unsupported number of stopbits: %r" % self._stopbits)

        # Map parity to UsbSerialPort constants
        if self._parity == 'N':
            parity = UsbSerialPort.PARITY_NONE
        elif self._parity == 'E':
            parity = UsbSerialPort.PARITY_EVEN
        elif self._parity == 'O':
            parity = UsbSerialPort.PARITY_ODD
        elif self._parity == 'M':
            parity = UsbSerialPort.PARITY_MARK
        elif self._parity == 'S':
            parity = UsbSerialPort.PARITY_SPACE
        else:
            raise ValueError("unsupported parity type: %r" % self._parity)

        # Set the parameters on the port
        self.mik3yPort.setParameters(self._baudrate, dataBits, stopBits, parity)
        self.mik3yPort.setDTR(True)
        self.mik3yPort.setRTS(True)

    def _update_rts_state(self):
        if not self.mik3yPort:
            raise SerialException("Port not open")
        self.mik3yPort.setRTS(bool(self._rts_state))

    def _update_dtr_state(self):
        if not self.mik3yPort:
            raise SerialException("Port not open")
        self.mik3yPort.setDTR(bool(self._dtr_state))

    def close(self):
        if self.is_open:
            if self.mik3yPort:
                self.mik3yPort.close()
                self.mik3yPort = None
            self.is_open = False

    def read(self, size=16 * 1024):
        if not self.mik3yPort:
            raise SerialException("Port not open")
        if size == -1:
            size = 16 * 1024
        data = bytearray(size)
        timeout = int(self._timeout * 1000) if self._timeout is not None else 0
        num_bytes_read = self.mik3yPort.read(data, timeout)
        return bytes(data[:num_bytes_read])

    def write(self, data):
        if not self.mik3yPort:
            raise SerialException("Port not open")
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError('expected bytes or bytearray, got %s' % type(data))
        timeout = int(self._timeout * 1000) if self._timeout is not None else 0
        self.mik3yPort.write(data, timeout)
        return len(data)

    def reset_input_buffer(self):
        if not self.mik3yPort:
            raise SerialException("Port not open")
        try:
            self.mik3yPort.purgeHwBuffers(True, False)
        except UnsupportedOperationException:
            print("Warning: Purging input buffer is not supported on this device.")

    def reset_output_buffer(self):
        if not self.mik3yPort:
            raise SerialException("Port not open")
        try:
            self.mik3yPort.purgeHwBuffers(False, True)
        except UnsupportedOperationException:
            print("Warning: Purging output buffer is not supported on this device.")

    def send_break(self, duration=0.25):
        if not self.mik3yPort:
            raise SerialException("Port not open")
        self.mik3yPort.setBreak(True)
        time.sleep(duration)
        self.mik3yPort.setBreak(False)

    def fileno(self):
        """\
        For easier use of the serial port instance with select.
        WARNING: this function is not portable to different platforms!
        """
        if not self.is_open:
            raise PortNotOpenError()
        return self.fd

    @property
    def in_waiting(self):
        if not self.mik3yPort:
            raise SerialException("Port not open")
        return -1

    @property
    def cts(self):
        if not self.mik3yPort:
            raise SerialException("Port not open")
        return self.mik3yPort.getCTS()

    @property
    def dsr(self):
        if not self.mik3yPort:
            raise SerialException("Port not open")
        return self.mik3yPort.getDSR()

    @property
    def ri(self):
        if not self.mik3yPort:
            raise SerialException("Port not open")
        return self.mik3yPort.getRI()

    @property
    def cd(self):
        if not self.mik3yPort:
            raise SerialException("Port not open")
        return self.mik3yPort.getCD()
