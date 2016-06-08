#!/usr/bin/env python
#
# This is a module that gathers a list of serial ports including details on
# GNU/Linux systems.
#
# This file is part of pySerial. https://github.com/pyserial/pyserial
# (C) 2011-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

import glob
import os
from serial.tools import list_ports_common


class SysFS(list_ports_common.ListPortInfo):
    """Wrapper for easy sysfs access and device info"""

    def __init__(self, device):
        super(SysFS, self).__init__(device)
        self.name = os.path.basename(device)
        self.usb_device_path = None
        if os.path.exists('/sys/class/tty/{}/device'.format(self.name)):
            self.device_path = os.path.realpath('/sys/class/tty/{}/device'.format(self.name))
            self.subsystem = os.path.basename(os.path.realpath(os.path.join(self.device_path, 'subsystem')))
        else:
            self.device_path = None
            self.subsystem = None
        # check device type
        if self.subsystem == 'usb-serial':
            self.usb_device_path = os.path.dirname(os.path.dirname(self.device_path))
        elif self.subsystem == 'usb':
            self.usb_device_path = os.path.dirname(self.device_path)
        else:
            self.usb_device_path = None
        # fill-in info for USB devices
        if self.usb_device_path is not None:
            self.vid = int(self.read_line(self.usb_device_path, 'idVendor'), 16)
            self.pid = int(self.read_line(self.usb_device_path, 'idProduct'), 16)
            self.serial_number = self.read_line(self.usb_device_path, 'serial')
            self.location = os.path.basename(self.usb_device_path)
            self.manufacturer = self.read_line(self.usb_device_path, 'manufacturer')
            self.product = self.read_line(self.usb_device_path, 'product')
            self.interface = self.read_line(self.device_path, 'interface')

        if self.subsystem in ('usb', 'usb-serial'):
            self.apply_usb_info()
        #~ elif self.subsystem in ('pnp', 'amba'):  # PCI based devices, raspi
        elif self.subsystem == 'pnp':  # PCI based devices
            self.description = self.name
            self.hwid = self.read_line(self.device_path, 'id')
        elif self.subsystem == 'amba':  # raspi
            self.description = self.name
            self.hwid = os.path.basename(self.device_path)

    def read_line(self, *args):
        """\
        Helper function to read a single line from a file.
        One or more parameters are allowed, they are joined with os.path.join.
        Returns None on errors..
        """
        try:
            with open(os.path.join(*args)) as f:
                line = f.readline().strip()
            return line
        except IOError:
            return None


def comports():
    devices = glob.glob('/dev/ttyS*')           # built-in serial ports
    devices.extend(glob.glob('/dev/ttyUSB*'))   # usb-serial with own driver
    devices.extend(glob.glob('/dev/ttyACM*'))   # usb-serial with CDC-ACM profile
    devices.extend(glob.glob('/dev/ttyAMA*'))   # ARM internal port (raspi)
    devices.extend(glob.glob('/dev/rfcomm*'))   # BT serial devices
    return [info
            for info in [SysFS(d) for d in devices]
            if info.subsystem != "platform"]    # hide non-present internal serial ports

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# test
if __name__ == '__main__':
    for port, desc, hwid in sorted(comports()):
        print("{}: {} [{}]".format(port, desc, hwid))
