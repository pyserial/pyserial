# This file is part of pySerial - Cross platform serial port support for Python
#
# SPDX-License-Identifier:    BSD-3-Clause

"""
Test the Win32 serial port naming.
"""

import os

import pytest

if os.name == "nt":
    from serial import serialwin32, win32

pytestmark = pytest.mark.skipif(os.name != "nt", reason="Windows only")


@pytest.mark.parametrize(
    "port, expected",
    (
        ("COM1", "COM1"),
        ("COM8", "COM8"),
        ("COM9", "COM9"),
        ("com3", "com3"),
        ("COM0", r"\\.\COM0"),
        ("com0", r"\\.\com0"),
        ("COM00", r"\\.\COM00"),
        ("COM01", r"\\.\COM01"),
        ("COM10", r"\\.\COM10"),
        ("COM255", r"\\.\COM255"),
        (r"\\.\COM1", r"\\.\COM1"),
        (r"\\.\COM0", r"\\.\COM0"),
        ("COM", "COM"),
        ("COMnotanumber", "COMnotanumber"),
        ("/dev/ttyS0", "/dev/ttyS0"),
    ),
)
def test_device_path(port, expected):
    """Verify that every port without an MS-DOS device alias is prefixed."""

    assert serialwin32.device_path(port) == expected


@pytest.mark.parametrize(
    "port, expected",
    (
        pytest.param("COM0", r"\\.\COM0", id="device-namespace"),
        pytest.param("COM1", "COM1", id="ms-dos-alias"),
    ),
)
def test_open_names_the_device(monkeypatch, port, expected):
    """Verify that `open()` hands the resolvable name to CreateFile."""

    names = []

    def create_file(name, *args):
        names.append(name)
        return win32.INVALID_HANDLE_VALUE

    monkeypatch.setattr(win32, "CreateFile", create_file)

    with pytest.raises(serialwin32.SerialException):
        serialwin32.Serial(port)

    assert names == [expected]
