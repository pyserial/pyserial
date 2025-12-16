# Copyright 2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: BSD-3-Clause

import json
import pathlib
import typing

import pytest


@pytest.fixture
def prepare_filesystem(fs):
    """Provide a helper function that creates a fake filesystem given a test asset."""

    def _prepare_filesystem(asset_path: str) -> dict[str, typing.Any]:
        path = pathlib.Path(__file__).parent.parent / asset_path
        fs.add_real_file(path)
        data = json.loads(path.read_text())

        for info in data["filesystem"]:
            if info["type"] == "char_device":
                fs.create_file(info["path"])
            if info["type"] == "file" and info["os_error"] is None:
                contents = "\n".join(info["contents"]).encode(info["encoding"])
                fs.create_file(info["path"], contents=contents)
            if info["type"] == "symlink":
                fs.create_symlink(info["path"], info["realpath"])

        return data

    return _prepare_filesystem
