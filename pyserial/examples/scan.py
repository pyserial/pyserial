#!/usr/bin/env python
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