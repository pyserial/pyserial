#!/usr/bin/env python
#
# This is a module that gathers a list of serial ports including details on
# GNU/Linux systems.
#
# This file is part of pySerial. https://github.com/pyserial/pyserial
# (C) 2011-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

from __future__ import absolute_import

import glob
import os

import subprocess

from serial.tools import list_ports_common

class DevInfo(list_ports_common.ListPortInfo):
    def __init__(self, line):
        self.props = {}
        for n, i in enumerate(line.split()):
            if n == 0:
                self.description = i
                continue
            f = i.split('=', maxsplit=1)
            if len(f) == 2:
                self.props[f[0]] = f[1]
            else:
                self.props[f[0]] = True
        self.device = "/dev/cua" + self.props["ttyname"]
        if "vendor" in self.props:
            self.vid = int(self.props["vendor"], 16)
            self.manufacturer = self.vid
        else:
            self.vid = 0
            self.manufacturer = "<generic>"
        if "product" in self.props:
            self.pid = int(self.props["product"], 16)
            self.product = "<none>"
        else:
            self.pid = 0
            self.product = "<none>"
        if "sernum" in self.props:
            self.serial_number = self.props["sernum"]
        else:
            self.serial_number = "none"
        if "ugen" in self.props:
            self.location = self.props["ugen"]
            self.subsystem = "usb"
            # print("PHK", type(self), self.props) 
            # self.apply_usb_info()
        else:
            self.subsystem = "uart"
            self.hwid = self.description

    def usb_description(self):
        return self.props["ugen"]

def comports(include_links=False):
    x = subprocess.run(["/usr/sbin/devinfo", "-rv"], capture_output=True)
    seen = set()
    for line in x.stdout.decode('utf-8').split('\n'):
        if "ttyname" in line:
            d = DevInfo(line)
            seen.add(d.device)
            yield d
    for fn in sorted(glob.glob("/dev/cua*[!.init][!.lock]")):
        if fn not in seen:
            d = DevInfo(fn[5:] + " ttyname=" + fn[8:])
            seen.add(d.device)
            yield d

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# test
if __name__ == '__main__':
    for info in sorted(comports()):
        print("{0}: {0.subsystem}".format(info))
