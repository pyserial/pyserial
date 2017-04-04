#!/usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Test serial.threaded related functionality.
"""

import os
import unittest
import serial
import serial.threaded
import struct
import time


# on which port should the tests be performed:
PORT = 'loop://'

class Test_threaded(unittest.TestCase):
    """Test serial.threaded related functionality"""

    def test_line_reader(self):
        """simple test of line reader class"""

        class TestLines(serial.threaded.LineReader):
            def __init__(self):
                super(TestLines, self).__init__()
                self.received_lines = []

            def handle_line(self, data):
                self.received_lines.append(data)

        ser = serial.serial_for_url(PORT, baudrate=115200, timeout=1)
        with serial.threaded.ReaderThread(ser, TestLines) as protocol:
            protocol.write_line('hello')
            protocol.write_line('world')
            time.sleep(1)
            self.assertEqual(protocol.received_lines, ['hello', 'world'])

    def test_framed_packet(self):
        """simple test of line reader class"""

        class TestFramedPacket(serial.threaded.FramedPacket):
            def __init__(self):
                super(TestFramedPacket, self).__init__()
                self.received_packets = []

            def handle_packet(self, packet):
                self.received_packets.append(packet)

            def send_packet(self, packet):
                self.transport.write(self.START)
                self.transport.write(packet)
                self.transport.write(self.STOP)

        ser = serial.serial_for_url(PORT, baudrate=115200, timeout=1)
        with serial.threaded.ReaderThread(ser, TestFramedPacket) as protocol:
            protocol.send_packet(b'1')
            protocol.send_packet(b'2')
            protocol.send_packet(b'3')
            time.sleep(1)
            self.assertEqual(protocol.received_packets, [b'1', b'2', b'3'])

    def test_structured_packet(self):
        """simple test of structured packet class"""

        class TestStructuredPacket(serial.threaded.StructuredPacket):

            DATA_SIZE = 8

            def __init__(self):
                super(TestStructuredPacket, self).__init__(self.DATA_SIZE)
                self.received_packets = []

            def handle_packet(self, packet):
                self.received_packets.append(packet)

            def send_packet(self, packet):
                self.transport.write(self.HEADER)
                self.transport.write(packet)

        ser = serial.serial_for_url(PORT, baudrate=115200, timeout=1)
        with serial.threaded.ReaderThread(ser, TestStructuredPacket) as protocol:
            protocol.send_packet(struct.pack("2I", *[1, 2]))
            protocol.send_packet(struct.pack("2I", *[3, 4]))
            time.sleep(1)
            self.assertEqual(protocol.received_packets,
                    [b'\x01\x00\x00\x00\x02\x00\x00\x00',
                        b'\x03\x00\x00\x00\x04\x00\x00\x00'])


if __name__ == '__main__':
    import sys
    sys.stdout.write(__doc__)
    if len(sys.argv) > 1:
        PORT = sys.argv[1]
    sys.stdout.write("Testing port: {!r}\n".format(PORT))
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
