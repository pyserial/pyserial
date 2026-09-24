"""Regression tests for read_until terminator validation."""

import pytest
import serial


def test_read_until_rejects_text_terminator_before_reading():
    with serial.serial_for_url('loop://', timeout=0) as port:
        with pytest.raises(TypeError, match='bytes'):
            port.read_until('STOP')


def test_read_until_rejects_empty_terminator_before_reading():
    with serial.serial_for_url('loop://', timeout=0) as port:
        with pytest.raises(ValueError, match='empty'):
            port.read_until(b'')


def test_read_until_accepts_bytes_like_terminators():
    with serial.serial_for_url('loop://', timeout=1) as port:
        for expected in (b'!', bytearray(b'!'), memoryview(b'!')):
            port.write(b'yes!')
            assert port.read_until(expected) == b'yes!'
