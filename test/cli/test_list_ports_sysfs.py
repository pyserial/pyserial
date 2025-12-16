# Copyright 2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: BSD-3-Clause

import sys

import pytest

import serial.tools.list_ports_linux

if sys.platform.lower().startswith('win32'):
    msg = "Skipping sysfs tests due to win32 sys.platform"
    pytest.skip(msg, allow_module_level=True)


def test_aten_uc_232a_pl2303(prepare_filesystem):
    """Test sysfs loading for the ATEN UC-232A USB-to-serial port adapter."""

    prepare_filesystem("assets/sysfs/ATEN--UC-232A.json")

    info = serial.tools.list_ports_linux.SysFS("/dev/ttyUSB0")

    assert info.device == "/dev/ttyUSB0"
    assert info.name == "ttyUSB0"
    assert info.description == "USB-Serial Controller D"
    assert info.hwid == "USB VID:PID=0557:2008 LOCATION=3-4.2.6"
    assert info.vid == 0x0557
    assert info.pid == 0x2008
    assert info.serial_number is None
    assert info.location == "3-4.2.6"
    assert info.manufacturer == "Prolific Technology Inc."
    assert info.product == "USB-Serial Controller D"
    assert info.interface is None
    assert info.usb_device_path == "/sys/devices/pci0000:00/0000:00:14.0/usb3/3-4/3-4.2/3-4.2.6"
    assert info.device_path == "/sys/devices/pci0000:00/0000:00:14.0/usb3/3-4/3-4.2/3-4.2.6/3-4.2.6:1.0/ttyUSB0"
    assert info.subsystem == "usb-serial"
    assert info.usb_interface_path == "/sys/devices/pci0000:00/0000:00:14.0/usb3/3-4/3-4.2/3-4.2.6/3-4.2.6:1.0"

    ports = serial.tools.list_ports_linux.comports()
    assert len(ports) == 1
    assert ports[0].device == "/dev/ttyUSB0"


def test_sparkfun_iot_redboard_rp2350(prepare_filesystem):
    """Test sysfs loading for the SparkFun IoT RedBoard RP2350."""

    prepare_filesystem("assets/sysfs/SparkFun--IoT-RedBoard-RP2350.json")

    info = serial.tools.list_ports_linux.SysFS("/dev/ttyACM0")

    assert info.device == "/dev/ttyACM0"
    assert info.name == "ttyACM0"
    assert info.description == "Board in FS mode - Board CDC"
    assert info.hwid == "USB VID:PID=1B4F:0047 SER=ffaae61c8e6fdd10 LOCATION=3-5:1.0"
    assert info.vid == 0x1B4F
    assert info.pid == 0x0047
    assert info.serial_number == "ffaae61c8e6fdd10"
    assert info.location == "3-5:1.0"
    assert info.manufacturer == "MicroPython"
    assert info.product == "Board in FS mode"
    assert info.interface == "Board CDC"
    assert info.usb_device_path == "/sys/devices/pci0000:00/0000:00:14.0/usb3/3-5"
    assert info.device_path == "/sys/devices/pci0000:00/0000:00:14.0/usb3/3-5/3-5:1.0"
    assert info.subsystem == "usb"
    assert info.usb_interface_path == "/sys/devices/pci0000:00/0000:00:14.0/usb3/3-5/3-5:1.0"

    ports = serial.tools.list_ports_linux.comports()
    assert len(ports) == 1
    assert ports[0].device == "/dev/ttyACM0"


def test_linux_6_14_0_tty_s0(prepare_filesystem):
    """Test sysfs loading of a Linux 6.14.0 builtin port."""

    prepare_filesystem("assets/sysfs/Linux-6.14.0--ttyS0.json")

    info = serial.tools.list_ports_linux.SysFS("/dev/ttyS0")

    assert info.device == "/dev/ttyS0"
    assert info.name == "ttyS0"
    assert info.description == "n/a"
    assert info.hwid == "n/a"
    assert info.vid is None
    assert info.pid is None
    assert info.serial_number is None
    assert info.location is None
    assert info.manufacturer is None
    assert info.product is None
    assert info.interface is None
    assert info.usb_device_path is None
    assert info.device_path == "/sys/devices/platform/serial8250/serial8250:0/serial8250:0.0"
    assert info.subsystem == "serial-base"
    assert info.usb_interface_path is None

    ports = serial.tools.list_ports_linux.comports()
    assert len(ports) == 1
    assert ports[0].device == "/dev/ttyS0"
