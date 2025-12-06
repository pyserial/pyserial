#!/usr/bin/env python
#
# This is a helper module for the various platform dependent list_port
# implementations.
#
# This file is part of pySerial. https://github.com/pyserial/pyserial
# (C) 2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

from __future__ import annotations

import glob
import os.path
import re
import typing


def numsplit(text: str) -> tuple[tuple[int, ...], ...]:
    """\
    Convert string into a list of texts and numbers in order to support a
    natural sorting.
    """
    result: list[tuple[int, ...]] = []
    for group in re.split(r'(\d+)', text):
        if group:
            try:
                result.append((int(group),))
            except ValueError:
                result.append(tuple(b for b in group.encode('utf-8')))
    return tuple(result)


class ListPortInfo:
    """Info collection base class for serial ports"""

    def __init__(self, device: str, skip_link_detection: bool = False) -> None:
        self.device = device
        self.name = os.path.basename(device)
        self.description = 'n/a'
        self.hwid = 'n/a'
        # USB specific data
        self.vid: int | None = None
        self.pid: int | None = None
        self.serial_number: str | None = None
        self.location: str | None = None
        self.manufacturer: str | None = None
        self.product: str | None = None
        self.interface: str | None = None
        # special handling for links
        if not skip_link_detection and os.path.islink(device):
            self.hwid = f'LINK={os.path.realpath(device)}'

    def usb_description(self) -> str:
        """return a short string to name the port based on USB info"""
        if self.interface is not None:
            return f'{self.product} - {self.interface}'
        elif self.product is not None:
            return self.product
        else:
            return self.name

    def usb_info(self) -> str:
        """return a string with USB related information about device"""
        return 'USB VID:PID={:04X}:{:04X}{}{}'.format(
            self.vid or 0,
            self.pid or 0,
            f' SER={self.serial_number}' if self.serial_number is not None else '',
            f' LOCATION={self.location}' if self.location is not None else '',
        )

    def __eq__(self, other: ListPortInfo | typing.Any) -> bool:
        return isinstance(other, ListPortInfo) and self.device == other.device

    def __hash__(self) -> int:
        return hash(self.device)

    def __lt__(self, other: ListPortInfo | typing.Any) -> bool:
        if isinstance(other, ListPortInfo):
            return numsplit(self.device) < numsplit(other.device)

        raise TypeError(
            'unorderable types: '
            f'{self.__class__.__name__}() and {other.__class__.__name__}()'
        )

    def __str__(self) -> str:
        return f'{self.device} - {self.description}'

    def __getitem__(self, index: int) -> str:
        """Item access: backwards compatible -> (port, desc, hwid)"""
        if index == 0:
            return self.device
        elif index == 1:
            return self.description
        elif index == 2:
            return self.hwid

        raise IndexError(f'{index} > 2')


def list_links(devices: set[str]) -> list[str]:
    """\
    search all /dev devices and look for symlinks to known ports already
    listed in devices.
    """
    links = []
    for device in glob.glob('/dev/*'):
        if os.path.islink(device) and os.path.realpath(device) in devices:
            links.append(device)
    return links
