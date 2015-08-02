#! /usr/bin/env python
# Python Serial Port Extension for Win32, Linux, BSD, Jython
# see __init__.py
#
# (C) 2001-2008 Chris Liechti <cliechti@gmx.net>
# this is distributed under a free software license, see license.txt

"""\
Some tests for the serial module.
Part of pyserial (http://pyserial.sf.net)  (C)2001-2009 cliechti@gmx.net

Intended to be run on different platforms, to ensure portability of
the code.

For all these tests a simple hardware is required.
Loopback HW adapter:
Shortcut these pin pairs:
 TX  <-> RX
 RTS <-> CTS
 DTR <-> DSR

On a 9 pole DSUB these are the pins (2-3) (4-6) (7-8)
"""

import unittest
import threading
import time
import sys
import serial

# on which port should the tests be performed:
PORT = 0

if sys.version_info >= (3, 0):
    def data(string):
        return bytes(string, 'latin1')
    bytes_0to255 = bytes(range(256))
else:
    def data(string): return string
    bytes_0to255 = ''.join([chr(x) for x in range(256)])


def segments(data, size=16):
    for a in range(0, len(data), size):
        yield data[a:a+size]


class Test4_Nonblocking(unittest.TestCase):
    """Test with timeouts"""
    timeout = 0

    def setUp(self):
        self.s = serial.serial_for_url(PORT, timeout=self.timeout)

    def tearDown(self):
        self.s.close()

    def test0_Messy(self):
        """NonBlocking (timeout=0)"""
        # this is only here to write out the message in verbose mode
        # because Test3 and Test4 print the same messages

    def test1_ReadEmpty(self):
        """timeout: After port open, the input buffer must be empty"""
        self.failUnlessEqual(self.s.read(1), data(''), "expected empty buffer")

    def test2_Loopback(self):
        """timeout: each sent character should return (binary test).
           this is also a test for the binary capability of a port."""
        for block in segments(bytes_0to255):
            length = len(block)
            self.s.write(block)
            # there might be a small delay until the character is ready (especially on win32)
            time.sleep(0.05)
            self.failUnlessEqual(self.s.inWaiting(), length, "expected exactly %d character for inWainting()" % length)
            self.failUnlessEqual(self.s.read(length), block)#, "expected a %r which was written before" % block)
        self.failUnlessEqual(self.s.read(1), data(''), "expected empty buffer after all sent chars are read")

    def test2_LoopbackTimeout(self):
        """timeout: test the timeout/immediate return.
        partial results should be returned."""
        self.s.write(data("HELLO"))
        time.sleep(0.1)    # there might be a small delay until the character is ready (especially on win32 and rfc2217)
        # read more characters as are available to run in the timeout
        self.failUnlessEqual(self.s.read(10), data('HELLO'), "expected the 'HELLO' which was written before")
        self.failUnlessEqual(self.s.read(1), data(''), "expected empty buffer after all sent chars are read")


class Test3_Timeout(Test4_Nonblocking):
    """Same tests as the NonBlocking ones but this time with timeout"""
    timeout = 1

    def test0_Messy(self):
        """Blocking (timeout=1)"""
        # this is only here to write out the message in verbose mode
        # because Test3 and Test4 print the same messages


class SendEvent(threading.Thread):
    def __init__(self, serial, delay=3):
        threading.Thread.__init__(self)
        self.serial = serial
        self.delay = delay
        self.x = threading.Event()
        self.stopped = 0
        self.start()

    def run(self):
        time.sleep(self.delay)
        self.x.set()
        if not self.stopped:
            self.serial.write(data("E"))
            self.serial.flush()

    def isSet(self):
        return self.x.isSet()

    def stop(self):
        self.stopped = 1
        self.x.wait()

class Test1_Forever(unittest.TestCase):
    """Tests a port with no timeout. These tests require that a
    character is sent after some time to stop the test, this is done
    through the SendEvent class and the Loopback HW."""
    def setUp(self):
        self.s = serial.serial_for_url(PORT, timeout=None)
        self.event = SendEvent(self.s)

    def tearDown(self):
        self.event.stop()
        self.s.close()

    def test2_ReadEmpty(self):
        """no timeout: after port open, the input buffer must be empty (read).
        a character is sent after some time to terminate the test (SendEvent)."""
        c = self.s.read(1)
        if not (self.event.isSet() and c == data('E')):
            self.fail("expected marker (evt=%r, c=%r)" % (self.event.isSet(), c))


class Test2_Forever(unittest.TestCase):
    """Tests a port with no timeout"""
    def setUp(self):
        self.s = serial.serial_for_url(PORT, timeout=None)

    def tearDown(self):
        self.s.close()

    def test1_inWaitingEmpty(self):
        """no timeout: after port open, the input buffer must be empty (inWaiting)"""
        self.failUnlessEqual(self.s.inWaiting(), 0, "expected empty buffer")

    def test2_Loopback(self):
        """no timeout: each sent character should return (binary test).
           this is also a test for the binary capability of a port."""
        for block in segments(bytes_0to255):
            length = len(block)
            self.s.write(block)
            # there might be a small delay until the character is ready (especially on win32 and rfc2217)
            time.sleep(0.05)
            self.failUnlessEqual(self.s.inWaiting(), length)#, "expected exactly %d character for inWainting()" % length)
            self.failUnlessEqual(self.s.read(length), block) #, "expected %r which was written before" % block)
        self.failUnlessEqual(self.s.inWaiting(), 0, "expected empty buffer after all sent chars are read")


class Test0_DataWires(unittest.TestCase):
    """Test modem control lines"""
    def setUp(self):
        self.s = serial.serial_for_url(PORT)

    def tearDown(self):
        self.s.close()

    def test1_RTS(self):
        """Test RTS/CTS"""
        self.s.setRTS(0)
        time.sleep(1.1)
        self.failUnless(not self.s.getCTS(), "CTS -> 0")
        self.s.setRTS(1)
        time.sleep(1.1)
        self.failUnless(self.s.getCTS(), "CTS -> 1")

    def test2_DTR(self):
        """Test DTR/DSR"""
        self.s.setDTR(0)
        time.sleep(1.1)
        self.failUnless(not self.s.getDSR(), "DSR -> 0")
        self.s.setDTR(1)
        time.sleep(1.1)
        self.failUnless(self.s.getDSR(), "DSR -> 1")

    def test3_RI(self):
        """Test RI"""
        self.failUnless(not self.s.getRI(), "RI -> 0")


class Test_MoreTimeouts(unittest.TestCase):
    """Test with timeouts"""
    def setUp(self):
        # create an closed serial port
        self.s = serial.serial_for_url(PORT, do_not_open=True)

    def tearDown(self):
        self.s.close()

    def test_WriteTimeout(self):
        """Test write() timeout."""
        # use xonxoff setting and the loop-back adapter to switch traffic on hold
        self.s.port = PORT
        self.s.writeTimeout = 1
        self.s.xonxoff = 1
        self.s.open()
        self.s.write(serial.XOFF)
        time.sleep(0.5) # some systems need a little delay so that they can react on XOFF
        t1 = time.time()
        self.failUnlessRaises(serial.SerialTimeoutException, self.s.write, data("timeout please"*200))
        t2 = time.time()
        self.failUnless( 0.9 <= (t2-t1) < 2.1, "Timeout not in the given interval (%s)" % (t2-t1))


if __name__ == '__main__':
    import sys
    sys.stdout.write(__doc__)
    if len(sys.argv) > 1:
        PORT = sys.argv[1]
    sys.stdout.write("Testing port: %r\n" % PORT)
    sys.argv[1:] = ['-v']
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
