#! /usr/bin/env python
#
# This file is part of pySerial - Cross platform serial port support for Python
# (C) 2017 Guillaume Galeazzi <guillaume.g@leazzi.ch>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Some tests for the serial module.
Part of pySerial (http://pyserial.sf.net)  (C)2001-2011 cliechti@gmx.net

Intended to be run on different platforms, to ensure portability of
the code.

Cover some of the aspects of context managment
"""

import unittest
import serial

# on which port should the tests be performed:
PORT = 'loop://'


class Test_Context(unittest.TestCase):
    """Test context"""

    def setUp(self):
        # create a closed serial port
        self.s = serial.serial_for_url(PORT)

    def tearDown(self):
        self.s.close()

    def test_with_idempotent(self):
        with self.s as stream:
            stream.write(b'1234')

        # do other stuff like calling an exe which use COM4

        with self.s as stream:
            stream.write(b'5678')


if __name__ == '__main__':
    import sys
    sys.stdout.write(__doc__)
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
