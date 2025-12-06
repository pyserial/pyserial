import dataclasses
import datetime
import pathlib
import platform
import sys
import typing


def get_metadata() -> dict[str, typing.Any]:
    uname = platform.uname()
    win32_ver = platform.win32_ver()
    mac_ver = platform.mac_ver()

    return {
        "context": {
            "$comment1": "------------------------------------------------------------",
            "$comment2": "Please fill out these fields manually to provide context.",
            "$comment3": "Do not copy-and-paste information returned by your system!",
            "$comment4": "The fields here provide external knowledge about the device,",
            "$comment5": "like the values printed on the board/chipset/device itself,",
            "$comment6": "or the commands you used to create a virtual device/port.",
            "$comment7": "------------------------------------------------------------",
            "description": "",
            "manufacturer": "",
            "model": "",
            "chipset": "",
            "serial_number": "",
            "commands": [
                "",
                "",
            ],
            "etc": "",
        },
        "generation_timestamp": datetime.datetime.now().strftime("%Y-%m-%d"),
        "platform": {
            "platform": platform.platform(),
            "python_implementation": platform.python_implementation(),
            "system": platform.system(),
            "uname": {
                "system": uname.system,
                # The `.node` attribute is deliberately excluded.
                "release": uname.release,
                "version": uname.version,
                "machine": uname.machine,
                "processor": uname.processor,
            },
            "version": platform.version(),
            "win32_ver": {
                "release": win32_ver[0],
                "version": win32_ver[1],
                "csd": win32_ver[2],
                "ptype": win32_ver[3],
            },
            "win32_edition": platform.win32_edition(),
            "mac_ver": {
                "release": mac_ver[0],
                "versioninfo": {
                    "version": mac_ver[1][0],
                    "dev_stage": mac_ver[1][1],
                    "non_release_version": mac_ver[1][2],
                },
                "machine": mac_ver[2],
            },
        },
        "sys": {
            "platform": sys.platform,
            "version": sys.version,
        },
    }


@dataclasses.dataclass(kw_only=True)
class PathInfo:
    path: pathlib.Path
    type: typing.Literal["char_device", "dir", "file", "symlink"]


@dataclasses.dataclass(kw_only=True)
class CharDeviceInfo(PathInfo):
    type: typing.Literal["char_device"] = "char_device"


@dataclasses.dataclass(kw_only=True)
class DirInfo(PathInfo):
    type: typing.Literal["dir"] = "dir"


@dataclasses.dataclass(kw_only=True)
class FileInfo(PathInfo):
    os_error: tuple[int, str] | None
    contents: list[str]
    is_truncated: bool
    type: typing.Literal["file"] = "file"
    encoding: typing.Literal["iso-8859-1"] = "iso-8859-1"


@dataclasses.dataclass(kw_only=True)
class SymlinkInfo(PathInfo):
    realpath: pathlib.Path
    type: typing.Literal["symlink"] = "symlink"
