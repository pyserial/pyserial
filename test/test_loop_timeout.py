# This file is part of pySerial - Cross platform serial port support for Python
# SPDX-License-Identifier: BSD-3-Clause

"""Read deadline coverage for the loopback URL handler."""

import queue

import pytest

import serial


def test_read_uses_remaining_timeout(monkeypatch):
    now = [10.0]
    waits = []
    monkeypatch.setattr('time.monotonic', lambda: now[0])
    monkeypatch.setattr('time.time', lambda: now[0])

    with serial.serial_for_url('loop://', timeout=1) as port:
        def get(timeout):
            waits.append(timeout)
            if len(waits) == 1:
                now[0] += 0.75
                return b'a'
            now[0] += timeout
            raise queue.Empty

        monkeypatch.setattr(port.queue, 'get', get)
        assert port.read(2) == b'a'

    assert waits == [1.0, 0.25]
    assert now[0] == 11.0


@pytest.mark.parametrize('timeout', [0, None, 1])
def test_read_available_data(timeout):
    with serial.serial_for_url('loop://', timeout=timeout) as port:
        port.write(b'ab')
        assert port.read(2) == b'ab'


def test_read_nonblocking_empty():
    with serial.serial_for_url('loop://', timeout=0) as port:
        assert port.read(2) == b''


def test_read_cancelled():
    with serial.serial_for_url('loop://') as port:
        port.cancel_read()
        assert port.read(2) == b''
