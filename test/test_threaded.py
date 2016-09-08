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
import time


# on which port should the tests be performed:
PORT = 'loop://'

class Test_asyncio(unittest.TestCase):
    """Test asyncio related functionality"""

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
            time.sleep(1)
            self.assertEqual(protocol.received_lines, ['hello'])


if __name__ == '__main__':
    import sys
    sys.stdout.write(__doc__)
    if len(sys.argv) > 1:
        PORT = sys.argv[1]
    sys.stdout.write("Testing port: {!r}\n".format(PORT))
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
