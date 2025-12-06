#!/usr/bin/env python
#
# Serial port enumeration. Console tool and backend selection.
#
# This file is part of pySerial. https://github.com/pyserial/pyserial
# (C) 2011-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

"""\
This module will provide a function called comports that returns an
iterable (generator or list) that will enumerate available com ports. Note that
on some systems non-existent ports may be listed.

Additionally a grep function is supplied that can be used to search for ports
based on their descriptions or hardware ID.
"""

import argparse
import os
import re
import sys
import typing

from serial.tools.list_ports_common import ListPortInfo

# Choose an implementation, depending on OS.
if os.name == 'nt':  # sys.platform == 'win32':  # pragma: no cover
    from serial.tools.list_ports_windows import comports
elif os.name == 'posix':  # pragma: no cover
    from serial.tools.list_ports_posix import comports
else:  # pragma: no cover
    raise ImportError(f"Sorry: no implementation for your platform ('{os.name}') available")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def grep(regexp: str, include_links: bool = False) -> typing.Iterable[ListPortInfo]:
    """\
    Search for ports using a regular expression. Port name, description and
    hardware ID are searched. The function returns an iterable that returns the
    same tuples as comport() would do.
    """
    r = re.compile(regexp, re.I)
    for info in comports(include_links):
        port, desc, hwid = info
        if r.search(port) or r.search(desc) or r.search(hwid):
            yield info


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def main() -> None:
    parser = argparse.ArgumentParser(description='Serial port enumeration')

    parser.add_argument(
        'regexp',
        nargs='?',
        help='only show ports that match this regex')

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='show more messages')

    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='suppress all messages')

    parser.add_argument(
        '-1', '--only-one',
        action='store_true',
        help='require exactly one matching entry, otherwise error')

    parser.add_argument(
        '-n',
        type=int,
        help='only output the N-th entry')

    parser.add_argument(
        '-s', '--include-links',
        action='store_true',
        help='include entries that are symlinks to real devices')

    args = parser.parse_args()

    # get list of ports
    if args.regexp:
        if not args.quiet:
            sys.stderr.write(f"Filtered list with regexp: {args.regexp!r}\n")
        found = list(grep(args.regexp, include_links=args.include_links))
    else:
        found = list(comports(include_links=args.include_links))
    found.sort()

    # filter ports if specified
    if args.only_one and len(found) != 1:
        sys.stderr.write("Error: {} serial ports{}{}{}\n".format(
            len(found) or "no",
            f" match {args.regexp!r}" if args.regexp else "",
            f": {found[0][0]}, {found[1][0]}" if found else "",
            ", ..." if len(found) > 2 else ""
        ))
        sys.exit(1)
    if args.n is not None:
        found = [found[args.n - 1]] if 1 <= args.n <= len(found) else []

    # list ports
    for port in found:
        sys.stdout.write(f"{port.device:20}\n")
        if args.verbose:
            sys.stdout.write(f"    desc: {port.description}\n")
            sys.stdout.write(f"    hwid: {port.hwid}\n")
    if not args.quiet:
        if found:
            sys.stderr.write(f"{len(found)} ports found\n")
        else:
            sys.stderr.write("no ports found\n")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# test
if __name__ == '__main__':  # pragma: no cover
    main()
