#! /usr/bin/env python
# encoding: utf-8
"""
Example of connecting to a USB serial port on Mac OS X 11.4.

Note that these drivers will likely be required:

https://www.silabs.com/products/mcu/Pages/USBtoUARTBridgeVCPDrivers.aspx#mac

"""
from __future__ import print_function

import sys
sys.path.insert(0, '..')

import serial
import time

port = "/dev/cu.SLAB_USBtoUART6"

try:
    ser = serial.Serial(port,
        baudrate = 9600,
        bytesize = serial.EIGHTBITS,
        parity = serial.PARITY_NONE,
        stopbits = serial.STOPBITS_ONE)

except serial.SerialException as e:
    """
    You may see an exception message such as: "[Errno 16] Resource busy: '/dev/cu.SLAB_USBtoUART6'".
    
    You can try the following to release the resource.
    
    $ sudo lsof | grep UART
    screen    2786          <username>    5u      CHR              17,13      0t189                 725 /dev/cu.SLAB_USBtoUART6
    $ kill -9 2786
    $ sudo lsof | grep UART
    $ 
    """

    print("Port " + port + " not available - %s" % e)

if ser.isOpen():
    ser.write("\r")
    time.sleep(0.3)
    response = ser.read(ser.inWaiting())
    print(response)