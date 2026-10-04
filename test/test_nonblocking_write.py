"""Tests for non-blocking POSIX writes when the output buffer is full."""

import errno

import pytest

from serial import serialposix


@pytest.mark.parametrize(
    "error_number",
    sorted({errno.EAGAIN, errno.EALREADY, errno.EWOULDBLOCK, errno.EINPROGRESS}),
)
def test_nonblocking_write_returns_zero_when_os_write_would_block(
    monkeypatch, error_number
):
    serial = serialposix.Serial(write_timeout=0)
    serial.is_open = True
    serial.fd = 42
    calls = []

    def write(_fd, _data):
        calls.append(1)
        raise OSError(error_number, "would block")

    monkeypatch.setattr(serialposix.os, "write", write)

    assert serial.write(b"full") == 0
    assert len(calls) == 1


def test_nonblocking_write_retries_interrupted_system_call(monkeypatch):
    serial = serialposix.Serial(write_timeout=0)
    serial.is_open = True
    serial.fd = 42
    calls = []

    def write(_fd, data):
        calls.append(1)
        if len(calls) == 1:
            raise OSError(errno.EINTR, "interrupted")
        return len(data)

    monkeypatch.setattr(serialposix.os, "write", write)

    assert serial.write(b"retry") == 5
    assert len(calls) == 2
