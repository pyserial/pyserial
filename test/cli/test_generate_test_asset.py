# Copyright 2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: BSD-3-Clause

import json
import pathlib

import pytest

import serial.tools.generate_test_asset
import serial.tools.generate_test_asset._common as common
import serial.tools.generate_test_asset._sysfs as sysfs


@pytest.fixture
def bogus_platform(monkeypatch):
    """Make the test asset generator call a static `get_info()` function.

    This allows cross-platform testing of argument parsing and output generation.
    Because of the types of the info values, it also tests
    """

    info = {
        "metadata": {},
        "more-information": {
            "dataclass": common.PathInfo(
                path=pathlib.Path("bogus"),
                type="file",
            ),
        },
    }
    monkeypatch.setattr("sys.platform", "bogus")
    monkeypatch.setattr(
        serial.tools.generate_test_asset,
        "_get_platform_specific_info_getter",
        lambda: (lambda *_: info),
    )


def test_get_metadata():
    """get_metadata() should not crash on any platform.

    This must be true even if the platform is not supported by pyserial.
    """

    metadata = common.get_metadata()
    assert "context" in metadata


def test_sysfs_get_info_no_devices_exist(fs):
    """Verify the behavior of `sysfs.get_info()` when no devices exist."""

    with pytest.raises(OSError, match="None of the given device paths appear to exist"):
        sysfs.get_info([])


def test_sysfs_get_info_target_is_file(fs):
    fs.create_file("bogus")

    with pytest.raises(OSError, match="not a character device"):
        sysfs.get_info(["bogus"])


def test_sysfs_get_info_target_is_directory(fs):
    fs.create_dir("bogus")

    with pytest.raises(OSError, match="is a directory"):
        sysfs.get_info(["bogus"])


def test_asset_generator_uses_stdout(fs, bogus_platform, monkeypatch, capsys):
    fs.create_file("bogus")

    # Patch the CLI arguments to write to STDOUT.
    monkeypatch.setattr("sys.argv", ["executable-name", "-o", "-", "bogus"])

    exit_code = serial.tools.generate_test_asset.main()
    assert exit_code == 0
    stdout, _ = capsys.readouterr()
    # The result should be parseable as JSON.
    assert isinstance(json.loads(stdout), dict)


def test_asset_generator_write_to_file(fs, bogus_platform, monkeypatch, capsys):
    fs.create_file("bogus")

    # Patch the CLI arguments to write to STDOUT.
    monkeypatch.setattr("sys.argv", ["executable-name", "-o", "output.json", "bogus"])

    exit_code = serial.tools.generate_test_asset.main()
    assert exit_code == 0
    stdout, _ = capsys.readouterr()
    assert stdout == ""

    # The result should be parseable as JSON.
    with open("output.json") as file:
        assert isinstance(json.loads(file.read()), dict)
