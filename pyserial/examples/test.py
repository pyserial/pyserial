#!/usr/bin/env python
"""Some Tests for the serial module.
part of pyserial (http://pyserial.sf.net)  (C)2002 cliechti@gmx.net

intended to be run on different platforms, to ensure portability of
the code.

for all these tests a simple hardware is required.
Loopback HW adapter:
shortcut these pin pairs on a 9 pole DSUB: (2-3) (4-6) (7-8)

 TX  -\
 RX  -/

 RTS -\
 CTS -/

 DTR -\
 DSR -/

 GND
 RI
"""

import unittest, threading, time
import serial

#of which port should the tests be performed:
PORT=0


class TestNonblocking(unittest.TestCase):
    """Test with timeouts"""
    timeout=0
    def setUp(self):
        self.s = serial.Serial(PORT,timeout=self.timeout)
    def tearDown(self):
        self.s.close()

    def test1_ReadEmpty(self):
        """After port open, the input buffer must be empty"""
        self.failUnless(self.s.read(1)=='', "expected empty buffer")
    def test2_Loopback(self):
        """With the Loopback HW, each sent character should return.
           this is also a test for the binary capability of a port."""
        for c in map(chr,range(256)):
            self.s.write(c)
            time.sleep(0.02)    #there might be a small delay until the character is ready (especialy on win32)
            self.failUnless(self.s.read(1)==c, "expected an '%s' which was written before" % c)
        self.failUnless(self.s.read(1)=='', "expected empty buffer after all sent chars are read")
    def test2_LoopbackTimeout(self):
        """test the timeout/immediate return, and that partial results are returned"""
        self.s.write("HELLO")
        time.sleep(0.02)    #there might be a small delay until the character is ready (especialy on win32)
        #read more characters as are available to run in the timeout
        self.failUnless(self.s.read(10)=='HELLO', "expected an 'HELLO' which was written before")
        self.failUnless(self.s.read(1)=='', "expected empty buffer after all sent chars are read")


class TestTimeout(TestNonblocking):
    """Same tests as the NonBlocking ones but this time with timeout"""
    timeout=1

class SendEvent(threading.Thread):
    def __init__(self, serial, delay=1):
        threading.Thread.__init__(self)
        self.serial = serial
        self.delay = delay
        self.x = threading.Event()
        self.stopped = 0
        self.start()
    def run(self):
        time.sleep(self.delay)
        if not self.stopped:
            self.serial.write("E")
        self.x.set()
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
        self.s = serial.Serial(PORT,timeout=None)
        self.event = SendEvent(self.s)
    def tearDown(self):
        self.event.stop()
        self.s.close()

    def test2_ReadEmpty(self):
        """After port open, the input buffer must be empty. a character is
        sent after some time to terminate the test (SendEvent)."""
        c = self.s.read(1)
        if not (self.event.isSet() and c =='E'):
            self.fail("expected marker")

class Test2_Forever(unittest.TestCase):
    """Tests a port with no timeout"""
    def setUp(self):
        self.s = serial.Serial(PORT,timeout=None)
    def tearDown(self):
        self.s.close()

    def test1_inWaitingEmpty(self):
        """After port open, the input buffer must be empty"""
        self.failUnless(self.s.inWaiting()==0, "expected empty buffer")

    def test2_Loopback(self):
        """With the Loopback HW, each sent character should return.
           this is also a test for the binary capability of a port."""
        for c in map(chr,range(256)):
            self.s.write(c)
            time.sleep(0.02)    #there might be a small delay until the character is ready (especialy on win32)
            self.failUnless(self.s.read(1)==c, "expected an '%s' which was written before" % c)
        self.failUnless(self.s.inWaiting()==0, "expected empty buffer after all sent chars are read")


class TestDataWires(unittest.TestCase):
    """Test modem control lines"""
    def setUp(self):
        self.s = serial.Serial(PORT)
    def tearDown(self):
        self.s.close()

    def test1_RTS(self):
        self.s.setRTS(0)
        self.failUnless(self.s.getCTS()==0, "CTS -> 0")
        self.s.setRTS(1)
        self.failUnless(self.s.getCTS()==0, "CTS -> 1")

    def test2_DTR(self):
        self.s.setDTR(0)
        self.failUnless(self.s.getDSR()==0, "DSR -> 0")
        self.s.setDTR(1)
        self.failUnless(self.s.getDSR()==0, "DSR -> 1")

##    def test3_RI(self):
##        self.failUnless(self.s.getRI()==0, "RI -> 0")

if __name__ == '__main__':
    # When this module is executed from the command-line, run all its tests
    unittest.main()
