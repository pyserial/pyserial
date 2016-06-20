#!/usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Test asyncio related functionality.
"""

import os
import unittest
import serial

# on which port should the tests be performed:
PORT = '/dev/ttyUSB0'

try:
    import asyncio
    import serial.aio
except (ImportError, SyntaxError):
    # not compatible with python 2.x
    pass
else:

    @unittest.skipIf(os.name != 'posix', "asyncio not supported on platform")
    class Test_asyncio(unittest.TestCase):
        """Test asyncio related functionality"""

        def setUp(self):
            self.loop = asyncio.get_event_loop()
            # create a closed serial port

        def tearDown(self):
            self.loop.close()

        def test_asyncio(self):
            TEXT = b'hello world\n'
            received = []
            actions = []

            class Output(asyncio.Protocol):
                def connection_made(self, transport):
                    self.transport = transport
                    actions.append('open')
                    transport.serial.rts = False
                    transport.write(TEXT)

                def data_received(self, data):
                    #~ print('data received', repr(data))
                    received.append(data)
                    if b'\n' in data:
                        self.transport.close()

                def connection_lost(self, exc):
                    actions.append('close')
                    asyncio.get_event_loop().stop()

                def pause_writing(self):
                    actions.append('pause')
                    print(self.transport.get_write_buffer_size())

                def resume_writing(self):
                    actions.append('resume')
                    print(self.transport.get_write_buffer_size())

            coro = serial.aio.create_serial_connection(self.loop, Output, PORT, baudrate=115200)
            self.loop.run_until_complete(coro)
            self.loop.run_forever()
            self.assertEqual(b''.join(received), TEXT)
            self.assertEqual(actions, ['open', 'close'])


if __name__ == '__main__':
    import sys
    sys.stdout.write(__doc__)
    if len(sys.argv) > 1:
        PORT = sys.argv[1]
    sys.stdout.write("Testing port: {!r}\n".format(PORT))
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
