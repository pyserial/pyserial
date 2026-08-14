# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

"""
Test Timeout helper class.
"""

from serial import serialutil


def test_simple_timeout(monkeypatch):
    """Test simple timeout"""

    # Force `time.monotonic()` to return a fixed value.
    monkeypatch.setattr("time.monotonic", lambda: 0.0)

    t = serialutil.Timeout(2)
    assert t.expired() is False
    assert t.time_left() == 2.0

    # Travel forward in time by 2.1 seconds.
    monkeypatch.setattr("time.monotonic", lambda: 2.1)
    assert t.expired() is True
    assert t.time_left() == 0.0


def test_non_blocking(monkeypatch):
    """Test nonblocking case (0)."""

    # Force `time.monotonic()` to return a fixed value.
    monkeypatch.setattr("time.monotonic", lambda: 100.0)

    t = serialutil.Timeout(0)
    assert t.is_non_blocking is True
    assert t.is_infinite is False
    assert t.expired() is True

    # Travel backwards in time to confirm that `expired()` isn't calculating anything.
    monkeypatch.setattr("time.monotonic", lambda: 0.0)
    assert t.expired() is True


def test_blocking(monkeypatch):
    """Test no timeout (None)"""

    # Force `time.monotonic()` to return a fixed value.
    monkeypatch.setattr("time.monotonic", lambda: 0.0)

    t = serialutil.Timeout(None)
    assert t.is_non_blocking is False
    assert t.is_infinite is True
    assert t.expired() is False

    # Test expiration behavior 100 years in the future.
    monkeypatch.setattr("time.monotonic", lambda: 3_153_600_000.0)
    assert t.expired() is False


def test_restart(monkeypatch):
    """Test the `restart()` method."""

    monkeypatch.setattr("time.monotonic", lambda: 0.0)
    t = serialutil.Timeout(1.0)
    monkeypatch.setattr("time.monotonic", lambda: 2.0)
    assert t.expired() is True

    t.restart(1.0)
    assert t.expired() is False
