#!/usr/bin/env python
"""Scan for serial ports
part of pyserial (http://pyserial.sf.net)  (C)2002 cliechti@gmx.net

the scan function of this module tries to open each port number
from 0 to 255 and it builds a list of those ports where this was
successful.
"""

from serial import Serial
from serial.serialutil import SerialException

def scan():
    """scan for available ports. return a list of tuples (num, name)"""
    available = []
    for i in range(256):
        try:
            s = Serial(i)
            available.append( (i, s.portstr))
            s.close()   #explicit close 'cause of delayed GC in java
        except SerialException:
            pass
    return available

if __name__=='__main__':
    print "Found ports:"
    for n,s in scan():
        print "(%d) %s" % (n,s)
