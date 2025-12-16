# Copyright 2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: BSD-3-Clause

import argparse
import dataclasses
import json
import pathlib
import sys
import textwrap
import typing

from . import _sysfs


def main() -> int:
    args = _get_parser().parse_args()

    try:
        get_info = _get_platform_specific_info_getter()
        output = get_info(args.devices)
    except OSError as e:
        print(e.args[0])
        return 1

    content = json.dumps(output, indent=2, cls=JsonEncoder)
    if args.output == pathlib.Path("-"):
        print(content)
    else:
        args.output.write_text(content)
    return 0


def _get_platform_specific_info_getter() -> (
    typing.Callable[[list[str]], dict[str, typing.Any]]
):
    sys_platform = sys.platform.lower()
    if sys_platform.startswith("linux"):
        return _sysfs.get_info

    raise OSError(f"This platform, '{sys.platform}', is not yet supported.")


def _get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=textwrap.dedent(
            """
            Generate an asset file suitable for inclusion in the pyserial test suite.
            """
        ),
        epilog=textwrap.dedent(
            """
            After generating this file, please edit the "context" section
            to provide information about the device, or the commands you used,
            or other information that is important to understand.

            Then, open an issue at:

                https://github.com/pyserial/pyserial/issues

            and attach this file without modification.
            Do not copy and paste the file into the issue.
            It must be attached to the issue as a downloadable file.
            """
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        required=True,
        help="The output path for the test asset file. Use '-' to write to STDOUT.",
        type=pathlib.Path,
    )
    parser.add_argument("devices", metavar="DEVICE", nargs="+", type=str)
    return parser


class JsonEncoder(json.JSONEncoder):
    def default(self, o: typing.Any) -> str | dict[str, typing.Any]:
        if dataclasses.is_dataclass(o) and not isinstance(o, type):
            return dataclasses.asdict(o)
        return str(o)
