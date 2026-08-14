#!/usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Test serial.threaded related functionality.
"""

import queue
import unittest

import serial
import serial.threaded

# on which port should the tests be performed:
PORT = 'loop://'


class TestThreaded(unittest.TestCase):
    """Test serial.threaded related functionality"""

    def test_line_reader(self):
        """simple test of line reader class"""

        line_queue = queue.Queue()

        class TestLines(serial.threaded.LineReader):
            def handle_line(self, data):
                line_queue.put(data)

        ser = serial.serial_for_url(PORT, baudrate=115200, timeout=1)
        with serial.threaded.ReaderThread(ser, TestLines) as protocol:
            protocol.write_line('hello')
            protocol.write_line('world')
            self.assertEqual(retrieve_item(line_queue), 'hello')
            self.assertEqual(retrieve_item(line_queue), 'world')

    def test_framed_packet(self):
        """simple test of line reader class"""

        packet_queue = queue.Queue()

        class TestFramedPacket(serial.threaded.FramedPacket):
            def handle_packet(self, packet):
                packet_queue.put(packet)

            def send_packet(self, packet):
                self.transport.write(self.START)
                self.transport.write(packet)
                self.transport.write(self.STOP)

        ser = serial.serial_for_url(PORT, baudrate=115200, timeout=1)
        with serial.threaded.ReaderThread(ser, TestFramedPacket) as protocol:
            protocol.send_packet(b'1')
            protocol.send_packet(b'2')
            protocol.send_packet(b'3')
            self.assertEqual(retrieve_item(packet_queue), b'1')
            self.assertEqual(retrieve_item(packet_queue), b'2')
            self.assertEqual(retrieve_item(packet_queue), b'3')


def retrieve_item(target_queue: queue.Queue) -> str | bytes:
    # Block for up to one second while trying to get an item from the queue.
    line = target_queue.get(timeout=1)
    target_queue.task_done()
    return line
