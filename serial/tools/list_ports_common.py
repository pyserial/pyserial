#!/usr/bin/env python
#
# This is a helper module for the various platform dependent list_port
# implementations.
#
# This file is part of pySerial. https://github.com/pyserial/pyserial
# (C) 2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
import re


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


class ListPortInfo(object):
    """Info collection base class for serial ports"""

    def __init__(self, device=None):
        self.device = device
        self.name = None
        self.description = 'n/a'
        self.hwid = 'n/a'
        # USB specific data
        self.vid = None
        self.pid = None
        self.serial_number = None
        self.location = None
        self.manufacturer = None
        self.product = None
        self.interface = None

    def usb_description(self):
        """return a short string to name the port based on USB info"""
        if self.interface is not None:
            return '{} - {}'.format(self.product, self.interface)
        elif self.product is not None:
            return self.product
        else:
            return self.name

    def usb_info(self):
        """return a string with USB related information about device"""
        return 'USB VID:PID={:04X}:{:04X}{}{}'.format(
            self.vid,
            self.pid,
            ' SER={}'.format(self.serial_number) if self.serial_number is not None else '',
            ' LOCATION={}'.format(self.location) if self.location is not None else '')

    def apply_usb_info(self):
        """update description and hwid from USB data"""
        self.description = self.usb_description()
        self.hwid = self.usb_info()

    def __eq__(self, other):
        return self.device == other.device

    def __lt__(self, other):
        return numsplit(self.device) < numsplit(other.device)

    def __str__(self):
        return '{} - {}'.format(self.device, self.description)

    def __getitem__(self, index):
        """Item access: backwards compatible -> (port, desc, hwid)"""
        if index == 0:
            return self.device
        elif index == 1:
            return self.description
        elif index == 2:
            return self.hwid
        else:
            raise IndexError('{} > 2'.format(index))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# test
if __name__ == '__main__':
    print(ListPortInfo('dummy'))
