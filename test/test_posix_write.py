# This file is part of pySerial - Cross platform serial port support for Python
# SPDX-License-Identifier: BSD-3-Clause
"""Completion, timeout and cancellation behavior of POSIX writes."""

import errno

import pytest

serialposix = pytest.importorskip('serial.serialposix', exc_type=ImportError)


@pytest.fixture
def port():
    serial_port = serialposix.Serial(write_timeout=1)
    serial_port.is_open = True
    serial_port.fd = 42
    serial_port.pipe_abort_write_r = 43
    yield serial_port
    serial_port.is_open = False
    serial_port.fd = None


@pytest.fixture
def clock(monkeypatch):
    now = [0.0]
    monkeypatch.setattr('time.monotonic', lambda: now[0])
    return now


def unexpected_call(*args, **kwargs):
    pytest.fail('No further I/O is needed after the payload is accepted')


def test_completed_write_returns_count_after_deadline(port, clock, monkeypatch):
    def write(fd, data):
        assert fd == port.fd
        clock[0] = 2.0
        return len(data)

    monkeypatch.setattr(serialposix.os, 'write', write)
    monkeypatch.setattr(serialposix.select, 'select', unexpected_call)
    assert port.write(b'complete') == 8


@pytest.mark.parametrize('timeout', (None, 1, 0))
def test_completed_write_does_not_wait_for_readiness(port, clock, monkeypatch, timeout):
    port._write_timeout = timeout
    monkeypatch.setattr(serialposix.os, 'write', lambda fd, data: len(data))
    monkeypatch.setattr(serialposix.select, 'select', unexpected_call)
    assert port.write(b'complete') == 8


def test_final_partial_write_completes_after_deadline(port, clock, monkeypatch):
    writes = []

    def write(fd, data):
        writes.append(data)
        if len(writes) == 1:
            return 2
        clock[0] = 2.0
        return len(data)

    selects = []

    def select(readers, writers, errors, timeout):
        selects.append(timeout)
        return [], writers, []

    monkeypatch.setattr(serialposix.os, 'write', write)
    monkeypatch.setattr(serialposix.select, 'select', select)
    assert port.write(b'abcdef') == 6
    assert writes == [b'abcdef', b'cdef']
    assert selects == [1.0]


def test_partial_write_still_raises_when_deadline_expires(port, clock, monkeypatch):
    def write(fd, data):
        clock[0] = 2.0
        return 2

    monkeypatch.setattr(serialposix.os, 'write', write)
    monkeypatch.setattr(serialposix.select, 'select', unexpected_call)
    with pytest.raises(serialposix.SerialTimeoutException):
        port.write(b'abcdef')


def test_partial_write_still_waits_and_times_out(port, clock, monkeypatch):
    monkeypatch.setattr(serialposix.os, 'write', lambda fd, data: 2)
    monkeypatch.setattr(serialposix.select, 'select', lambda *args: ([], [], []))
    with pytest.raises(serialposix.SerialTimeoutException):
        port.write(b'abcdef')


def test_cancel_pending_write_preserves_existing_result(port, clock, monkeypatch):
    reads = []

    def read(fd, size):
        reads.append((fd, size))
        return b'x'

    monkeypatch.setattr(serialposix.os, 'write', lambda fd, data: 2)
    monkeypatch.setattr(serialposix.os, 'read', read)
    monkeypatch.setattr(serialposix.select, 'select', lambda *args: ([43], [], []))
    assert port.write(b'abcdef') == 0
    assert reads == [(43, 1000)]


def test_interrupted_write_is_retried(port, clock, monkeypatch):
    writes = []

    def write(fd, data):
        writes.append(data)
        if len(writes) == 1:
            raise OSError(errno.EINTR, 'interrupted')
        return len(data)

    monkeypatch.setattr(serialposix.os, 'write', write)
    monkeypatch.setattr(serialposix.select, 'select', lambda readers, writers, *args: ([], writers, []))
    assert port.write(b'retry') == 5
    assert writes == [b'retry', b'retry']


def test_would_block_still_obeys_deadline(port, clock, monkeypatch):
    def write(fd, data):
        clock[0] = 2.0
        raise OSError(errno.EAGAIN, 'would block')

    monkeypatch.setattr(serialposix.os, 'write', write)
    with pytest.raises(serialposix.SerialTimeoutException):
        port.write(b'pending')


@pytest.mark.parametrize('written', (0, 2))
def test_nonblocking_write_preserves_short_count(port, monkeypatch, written):
    port._write_timeout = 0
    monkeypatch.setattr(serialposix.os, 'write', lambda fd, data: written)
    monkeypatch.setattr(serialposix.select, 'select', unexpected_call)
    assert port.write(b'abcdef') == written


def test_empty_write_returns_zero_without_io(port, monkeypatch):
    monkeypatch.setattr(serialposix.os, 'write', unexpected_call)
    monkeypatch.setattr(serialposix.select, 'select', unexpected_call)
    assert port.write(b'') == 0


def test_closed_port_still_raises(port, monkeypatch):
    port.is_open = False
    monkeypatch.setattr(serialposix.os, 'write', unexpected_call)
    with pytest.raises(serialposix.PortNotOpenError):
        port.write(b'')


def test_write_error_is_preserved(port, monkeypatch):
    def write(fd, data):
        raise OSError(errno.EIO, 'I/O error')

    monkeypatch.setattr(serialposix.os, 'write', write)
    with pytest.raises(serialposix.SerialException) as error:
        port.write(b'failed')
    assert error.value.errno == errno.EIO
