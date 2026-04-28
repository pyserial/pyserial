#!/usr/bin/env python
#
# This is a module that gathers a list of serial ports including details on
# FreeBSD systems, using devinfo(8) to discover USB device information.
#
# This file is part of pySerial. https://github.com/pyserial/pyserial
# (C) 2011-2015 Chris Liechti <cliechti@gmx.net>
# FreeBSD support by:
#  Poul-Henning Kamp <phk@FreeBSD.org> and
#  Kevin Bowling <kbowling@FreeBSD.org>
# SPDX-License-Identifier:    BSD-3-Clause

from __future__ import absolute_import

import glob
import re
import subprocess

from serial.tools import list_ports_common


class DevInfo(list_ports_common.ListPortInfo):
    """Collect serial port info from FreeBSD devinfo(8) output."""

    def __init__(self, device, props=None, usb_desc=None):
        super(DevInfo, self).__init__(device, skip_link_detection=True)
        self.props = props or {}

        if "vendor" in self.props:
            self.vid = int(self.props["vendor"], 16)
        if "product" in self.props:
            self.pid = int(self.props["product"], 16)
        if "sernum" in self.props:
            self.serial_number = self.props["sernum"].strip('"')

        # The USB description from devinfo contains the combined
        # iManufacturer and iProduct strings: "Manufacturer Product"
        # We cannot reliably split them, so store the combined text
        # as product.  VID/PID matching is the reliable identification
        # method on FreeBSD.
        if usb_desc:
            self.product = usb_desc

        if "ugen" in self.props:
            self.location = self.props["ugen"]
            self.subsystem = "usb"
            self.apply_usb_info()
        else:
            self.subsystem = "uart"
            self.description = device


def _parse_devinfo_line(line):
    """Parse a devinfo -rv output line containing ttyname.

    Example line:
        umodem0 <Keir Fraser Greaseweazle, class 2/0, rev 2.00/1.00, \
            addr 2> pnpinfo vendor=0x1209 product=0x4d69 ... ttyname=U0 \
            ... ugen=ugen1.3

    Returns (device_path, props_dict, usb_description) or None.
    """
    props = {}
    usb_desc = None

    # Match the full devinfo format with angle-bracket USB description
    m = re.match(r'\s*\S+\s+<(?P<desc_text>[^>]*)>.*?pnpinfo\s+(?P<props_text>.*)', line)
    if m:
        desc_text = m.group('desc_text')
        # Extract the human-readable part before ", class "
        desc_parts = desc_text.split(', class ')
        if desc_parts:
            usb_desc = desc_parts[0].strip()
        props_text = m.group('props_text')
    else:
        props_text = line

    # Parse key=value pairs from pnpinfo or fallback line
    for token in props_text.split():
        kv = token.split('=', maxsplit=1)
        if len(kv) == 2:
            props[kv[0]] = kv[1]

    if "ttyname" not in props:
        return None

    device = "/dev/cua" + props["ttyname"]
    return device, props, usb_desc


def comports(include_links=False):
    """Return serial ports discovered via devinfo(8) and /dev scanning."""
    seen = set()

    try:
        result = subprocess.run(
            ["/usr/sbin/devinfo", "-rv"],
            capture_output=True,
            timeout=5,
        )
        for line in result.stdout.decode('utf-8', errors='replace').split('\n'):
            if "ttyname" not in line:
                continue
            parsed = _parse_devinfo_line(line)
            if parsed is None:
                continue
            device, props, usb_desc = parsed
            info = DevInfo(device, props, usb_desc)
            seen.add(device)
            yield info
    except (OSError, subprocess.TimeoutExpired):
        pass

    # Pick up any /dev/cua* devices not found via devinfo
    devices = set(glob.glob("/dev/cua*[!.init][!.lock]"))
    if include_links:
        devices.update(list_ports_common.list_links(devices))
    for fn in sorted(devices):
        if fn not in seen:
            info = DevInfo(fn)
            seen.add(fn)
            yield info


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# test
if __name__ == '__main__':
    for info in sorted(comports()):
        print("{}: {} [{}]".format(info.device, info.description, info.hwid))
