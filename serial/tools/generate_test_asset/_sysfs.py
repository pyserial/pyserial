# Copyright 2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: BSD-3-Clause

"""
Generate an asset file suitable for inclusion in the test suite.

The test suite relies on asset files to mock out system calls,
and this script generates such an asset file
for operating systems that expose serial ports through the filesystem.
"""

import pathlib
import typing

from ._common import (
    CharDeviceInfo,
    DirInfo,
    FileInfo,
    PathInfo,
    SymlinkInfo,
    get_metadata,
)


def get_info(targets: list[str]) -> dict[str, typing.Any]:
    output: dict[str, typing.Any] = {
        "metadata": get_metadata(),
        "filesystem": [],
    }

    # Get basic device info.
    paths: list[tuple[int, pathlib.Path]] = [(0, pathlib.Path("/proc/tty/drivers"))]
    devices = [pathlib.Path(device) for device in sorted(set(targets))]
    while devices:
        device = devices.pop(0)
        if not device.exists():
            continue

        info = _get_device_info(device)
        output["filesystem"].append(info)
        if isinstance(info, SymlinkInfo):
            devices.append(info.realpath)
            continue

        # If a sysfs entry exists, add it for subsequent follow-up.
        sysfs_entry = pathlib.Path("/sys/class/tty") / device.name
        if not sysfs_entry.exists():
            continue

        paths.append((1, sysfs_entry))

        # Resolve the `.../device` path and append its two ancestor directories.
        # Recursion is disabled by setting the recursion depth to 0.
        _resolved_path = (sysfs_entry / "device").resolve()
        paths.append((0, _resolved_path))
        paths.append((0, _resolved_path.parent))
        paths.append((0, _resolved_path.parent.parent))

    if not output["filesystem"]:
        raise OSError("None of the given device paths appear to exist.")

    # Get sysfs info.
    # sysfs is recursive, so recursion depth and already-seen files are tracked.
    paths_seen: set[pathlib.Path] = set()
    while paths:
        depth, path = paths.pop(0)
        if path in paths_seen:
            continue
        if not path.exists():
            continue
        paths_seen.add(path)

        info = _get_path_info(path)
        output["filesystem"].append(info)
        if isinstance(info, SymlinkInfo) and depth >= 0:
            paths.append((depth - 1, info.realpath))
        elif isinstance(info, DirInfo) and depth >= 0:
            paths.extend((depth - 1, entry) for entry in info.path.iterdir())

    # Sort the paths, starting with the devices the user specified.
    output["filesystem"].sort(
        key=lambda item: (str(item.path) not in targets, item.path),
    )

    return output


def _get_device_info(device: pathlib.Path) -> PathInfo:
    if device.is_dir():
        raise OSError(f"'{device}' is a directory and cannot be scanned.")
    if device.is_symlink():
        return _get_path_info(device)
    if not device.is_char_device():
        raise OSError(f"'{device}' is not a character device and cannot be scanned.")
    return _get_path_info(device)


def _get_path_info(path: pathlib.Path) -> PathInfo:
    if path.is_symlink():
        return SymlinkInfo(
            path=path.absolute(),
            realpath=path.resolve(),
        )
    if path.is_dir(follow_symlinks=False):
        return DirInfo(path=path.absolute())
    if path.is_char_device():
        return CharDeviceInfo(path=path.absolute())

    # Files
    try:
        with path.open("rb") as file:
            raw_contents = file.read(10_001)
    except OSError as error:
        raw_contents = b""
        os_error: tuple[typing.Any, ...] | None = error.args
    else:
        os_error = None

    # Truncate if necessary.
    is_truncated = False
    if len(raw_contents) > 10_000:
        is_truncated = True
        raw_contents = raw_contents[:10_000]

    contents = raw_contents.decode("iso-8859-1").split("\n")
    return FileInfo(
        path=path.absolute(),
        os_error=os_error,
        contents=contents,
        is_truncated=is_truncated,
    )
