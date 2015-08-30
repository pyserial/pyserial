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
import os
import re
import subprocess


def read_command(argv):
    """run a command and return its output"""
    try:
        return subprocess.check_output(argv, stderr=subprocess.STDOUT).strip().decode('ascii', 'replace')
    except subprocess.SubprocessError as e:
        raise IOError('command %r failed: %s' % (argv, e))


def read_line(*args):
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


def re_group(regexp, text):
    """search for regexp in text, return 1st group on match"""
    m = re.search(regexp, text)
    if m:
        return m.group(1)
    else:
        return None


# try to extract descriptions from sysfs. this was done by experimenting,
# no guarantee that it works for all devices or in the future...

def usb_sysfs_hw_string(sysfs_path):
    """given a path to a usb device in sysfs, return a string describing it"""
    bus, dev = os.path.basename(os.path.realpath(sysfs_path)).split('-')
    snr = read_line(sysfs_path, 'serial')
    if snr is not None:
        snr_txt = ' SNR=%s' % (snr,)
    else:
        snr_txt = ''
    return 'USB VID:PID=%s:%s%s' % (
            read_line(sysfs_path, 'idVendor'),
            read_line(sysfs_path, 'idProduct'),
            snr_txt
            )


def usb_lsusb_string(sysfs_path):
    base = os.path.basename(os.path.realpath(sysfs_path))
    bus = base.split('-')[0]
    try:
        dev = int(read_line(sysfs_path, 'devnum'))
        desc = read_command(['lsusb', '-v', '-s', '%s:%s' % (bus, dev)])
    except IOError:
        return base
    else:
        # descriptions from device
        iManufacturer = re_group('iManufacturer\s+\w+ (.+)', desc)
        iProduct = re_group('iProduct\s+\w+ (.+)', desc)
        iSerial = re_group('iSerial\s+\w+ (.+)', desc) or ''
        # descriptions from kernel
        idVendor = re_group('idVendor\s+0x\w+ (.+)', desc)
        idProduct = re_group('idProduct\s+0x\w+ (.+)', desc)
        # create descriptions. prefer text from device, fall back to the others
        return '%s %s %s' % (iManufacturer or idVendor, iProduct or idProduct, iSerial)


def describe(device):
    """\
    Get a human readable description.
    For USB-Serial devices try to run lsusb to get a human readable description.
    For USB-CDC devices read the description from sysfs.
    """
    base = os.path.basename(device)
    # USB-Serial devices
    sys_dev_path = '/sys/class/tty/%s/device/driver/%s' % (base, base)
    if os.path.exists(sys_dev_path):
        sys_usb = os.path.dirname(os.path.dirname(os.path.realpath(sys_dev_path)))
        return usb_lsusb_string(sys_usb)
    # USB-CDC devices
    sys_dev_path = '/sys/class/tty/%s/device/interface' % (base,)
    if os.path.exists(sys_dev_path):
        return read_line(sys_dev_path)
    # USB Product Information
    sys_dev_path = '/sys/class/tty/%s/device' % (base,)
    if os.path.exists(sys_dev_path):
        product_name_file = os.path.dirname(os.path.realpath(sys_dev_path)) + "/product"
        if os.path.exists(product_name_file):
            return read_line(product_name_file)
    return base


def hwinfo(device):
    """Try to get a HW identification using sysfs"""
    base = os.path.basename(device)
    if os.path.exists('/sys/class/tty/%s/device' % (base,)):
        # PCI based devices
        sys_id_path = '/sys/class/tty/%s/device/id' % (base,)
        if os.path.exists(sys_id_path):
            return read_line(sys_id_path)
        # USB-Serial devices
        sys_dev_path = '/sys/class/tty/%s/device/driver/%s' % (base, base)
        if os.path.exists(sys_dev_path):
            sys_usb = os.path.dirname(os.path.dirname(os.path.realpath(sys_dev_path)))
            return usb_sysfs_hw_string(sys_usb)
        # USB-CDC devices
        if base.startswith('ttyACM'):
            sys_dev_path = '/sys/class/tty/%s/device' % (base,)
            if os.path.exists(sys_dev_path):
                return usb_sysfs_hw_string(sys_dev_path + '/..')
    return 'n/a'    # XXX directly remove these from the list?


def comports():
    devices = glob.glob('/dev/ttyS*')           # built-in serial ports
    devices.extend(glob.glob('/dev/ttyUSB*'))   # usb-serial with own driver
    devices.extend(glob.glob('/dev/ttyACM*'))   # usb-serial with CDC-ACM profile
    devices.extend(glob.glob('/dev/rfcomm*'))   # BT serial devices
    return [(d, describe(d), hwinfo(d)) for d in devices]

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# test
if __name__ == '__main__':
    for port, desc, hwid in sorted(comports()):
        print("%s: %s [%s]" % (port, desc, hwid))
