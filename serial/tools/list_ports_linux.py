#!/usr/bin/env python
#
# portable serial port access with python
#
# This is a module that gathers a list of serial ports including details on
# GNU/Linux systems.
# The comports function is expected to return an iterable that yields tuples of
# 3 strings: port name, human readable description and a hardware ID.
#
# (C) 2011-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

import glob
import re
import os


def numsplit(text):
    """\
    Convert string into a list of texts and numbers in order to support a
    natural sorting.
    """
    result = []
    for group in re.split(r'(\d+)', text):
        if group:
            try:
                group = int(group)
            except ValueError:
                pass
            result.append(group)
    return result


class SysFS(object):
    """Wrapper for easy sysfs access and device info"""

    def __init__(self, dev_path):
        self.dev = dev_path
        self.name = os.path.basename(self.dev)
        self.subsystem = None
        self.device_path = None
        self.usb_device_path = None
        if os.path.exists('/sys/class/tty/%s/device' % (self.name,)):
            self.device_path = os.path.realpath('/sys/class/tty/%s/device' % (self.name,))
            self.subsystem = os.path.basename(os.path.realpath(os.path.join(self.device_path, 'subsystem')))
        if self.subsystem == 'usb-serial':
            self.usb_device_path = os.path.dirname(os.path.dirname(self.device_path))
        elif self.subsystem == 'usb':
            self.usb_device_path = os.path.dirname(self.device_path)
        else:
            self.usb_device_path = None
        #~ print repr(self.__dict__)
        if self.usb_device_path is not None:
            self.vid = self.read_line(self.usb_device_path, 'idVendor').upper()
            self.pid = self.read_line(self.usb_device_path, 'idProduct').upper()
            self.serial = self.read_line(self.usb_device_path, 'serial')
            self.location = os.path.basename(self.usb_device_path)
        else:
            self.vid = None
            self.pid = None
            self.serial = None
            self.location = None

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

    def describe(self):
        if self.subsystem == 'usb-serial':
            return self.read_line(self.usb_device_path, 'product')
        elif self.subsystem == 'usb':  # CDC/ACM devices
            interface = self.read_line(self.device_path, 'interface')
            if interface is not None:
                return interface
            else:
                return self.read_line(self.usb_device_path, 'product')
        elif self.subsystem == 'pnp':  # PCI based devices
            return self.name
        elif self.subsystem == 'amba':  # raspi
            return self.name
        else:
            return 'n/a'

    def describe_full(self):
        """Get a human readable string"""
        if self.subsystem == 'usb-serial':
            return '{} - {}'.format(
                    self.read_line(self.usb_device_path, 'manufacturer'),
                    self.read_line(self.usb_device_path, 'product'),
                    )
        elif self.subsystem == 'usb':  # CDC/ACM devices
            interface = self.read_line(self.device_path, 'interface')
            return '{} - {}{}'.format(
                    self.read_line(self.usb_device_path, 'manufacturer'),
                    self.read_line(self.usb_device_path, 'product'),
                    ' - {}'.format(interface) if interface is not None else '',
                    )
        elif self.subsystem == 'pnp':  # PCI based devices
            return self.name
        elif self.subsystem == 'amba':  # raspi
            return self.name
        else:
            return 'n/a'

    def hwinfo(self):
        """Get a hardware description string"""
        if self.subsystem in ('usb', 'usb-serial'):
            return 'USB VID:PID={}:{}{}{}'.format(
                    self.vid,
                    self.pid,
                    ' SER={}'.format(self.serial) if self.serial is not None else '',
                    ' LOCATION={}'.format(self.location) if self.location is not None else '',
                    )
        elif self.subsystem == 'pnp':  # PCI based devices
            return self.read_line(self.device_path, 'id')
        elif self.subsystem == 'amba':  # raspi
            return os.path.basename(self.device_path)
        else:
            return 'n/a'

    def __eq__(self, other):
        return self.dev == other.dev

    def __lt__(self, other):
        return numsplit(self.dev) < numsplit(other.dev)

    def __getitem__(self, index):
        """Item access: backwards compatible -> (port, desc, hwid)"""
        if index == 0:
            return self.dev
        elif index == 1:
            return self.describe()
        elif index == 2:
            return self.hwinfo()
        else:
            raise IndexError('{} > 2'.format(index))


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
        print("%s: %s [%s]" % (port, desc, hwid))
