#!/usr/bin/env python
import unittest
import serial, time

#of which port should the tests be performed:
PORT=0

#for all these tests a simple hardware is requires.
#Loopback adapter:
#shortcut these pin pairs on a 9 pole DSUB: (2-3) (4-6) (7-8)
#
# TX  -\
# RX  -/
#
# RTS -\
# CTS -/
#
# DTR -\
# DSR -/
#
# GND
# RI
#

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
        """With the Loopback HW, heach sent character should return"""
        for c in map(chr,range(256)):
            self.s.write(c)
            time.sleep(0.02)    #there migh be a small delay until the character is ready
            self.failUnless(self.s.read(1)==c, "expected an '%s' which was written before" % c)
        self.failUnless(self.s.read(1)=='', "expected empty buffer after all sent chars are read")
    def test2_LoopbackTimeout(self):
        """test the timeout/immediate return, and that partial results are returned"""
        self.s.write("HELLO")
        time.sleep(0.02)    #there migh be a small delay until the character is ready
        #read more characters as are available to run in the timeout
        self.failUnless(self.s.read(10)=='HELLO', "expected an 'HELLO' wich was written before")
        self.failUnless(self.s.read(1)=='', "expected empty buffer after all sent chars are read")


class TestTimeout(TestNonblocking):
    """Same tests as the NonBlocking ones but this time with timeout"""
    timeout=1

class TestForever(unittest.TestCase):
    """Tests for a posrt with no timeout"""


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
