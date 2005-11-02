#!/usr/bin/env python
# character LCD example for pyparallel
#
#(C) 2002 Chris Liechti <cliechti@gmx.net>
# this is distributed under a free software license, see license.txt

import sys, time
sys.path.insert(0, '..')
import parallel

LCDON           = 0x01 #0x00000001 Switch on  display
LCDOFF          = 0x08 #0x00001000 Switch off display
LCDCLEAR        = 0x01 #0x00000001
LCDLINE1        = 0x80 #0x10000000
LCDLINE2        = 0xc0 #0x11000000
LCDCURSORON     = 0x0f #0x00001111 turn on cursor blinking
LCDCURSOROFF    = 0x0c #0x00001100 Disable cursor blinking. The cursor is hidden.
LCDCGADRSET     = 0x40 #0b01000000
LCDDDADRSET     = 0x80 #0b10000000
LCD2LINES       = 0x28 #0b00101000 Set display mode to two lines.
LCD8BITS        = 0x30 #0b00110000 select 8 Bit interface
LCD4BITS        = 0x20 #0b00100000 select 4 Bit interface
LCD_DATA_OFF    = 0x05 #0x00000101 mask used to clear the data lines

LCD_RS          = 1<<1
LCD_RW          = 1<<2
LCD_E           = 1<<3
LCD_D4          = 1<<4
LCD_D5          = 1<<5
LCD_D6          = 1<<6
LCD_D7          = 1<<7


class FourBitIO(object):
    def __init__(self):
        self.data = 0
        
        self.out(0)                 #reset pins
        time.sleep(0.050)           #wait more than 30ms
        #send the reset sequece (3 times the same pattern)
        self.out(LCD8BITS)          #set 8 bit interface
        self.toggleE()              #toggle LCD_E, the enable pin
        time.sleep(0.005)           #wait a bit
        self.toggleE()              #toggle LCD_E, the enable pin
        time.sleep(0.005)           #wait a bit
        self.toggleE()              #toggle LCD_E, the enable pin
        time.sleep(0.005)           #wait a bit
        
        self.out(LCD4BITS)          #now set up the 4 bit interface
        self.toggleE()              #toggle LCD_E, the enable pin
        time.sleep(0.002)           #wait until instr is finished
        self.instr(LCD2LINES)    #set 2 lines display
        self.instr(LCDCURSOROFF) #hide cursor
        self.instr(LCDCLEAR)     #clear display

    #my connector has the wrong pinorder....
    #better swap them in software than to solder ;-)
    def reveseout(self, x):
        r = ((x & (1<<0) and 1) << 7) |\
            ((x & (1<<1) and 1) << 6) |\
            ((x & (1<<2) and 1) << 5) |\
            ((x & (1<<3) and 1) << 4) |\
            ((x & (1<<4) and 1) << 3) |\
            ((x & (1<<5) and 1) << 2) |\
            ((x & (1<<6) and 1) << 1) |\
            ((x & (1<<7) and 1) << 0)
        #print "%02x" % r, "%02x" %x
        self.p.setData(r)
        
    def toggleE(self):
        """toggle enable pin"""
        self.data |= LCD_E;         #toggle LCD_E, the enable pin
        self.reveseout(self.data)
        self.data &= ~LCD_E;        #back to inactive position
        self.reveseout(self.data)

    def out(self, data):
        """set data to LCD port"""
        self.data = data
        self.reveseout(self.data)

    def instr(self, cmd):
        """send instruction byte to LCD"""
        self.out(cmd & 0xf0)        #output upper nibble
        self.toggleE()              #toggle LCD_E, the enable pin
        self.out((cmd << 4) & 0xf0) #and then the lower nibble
        self.toggleE()              #toggle LCD_E, the enable pin
        time.sleep(0.001)           #wait until instr is finished

    def putc(self, c):
        """send a data byte to the LCD"""
        c = ord(c)
        self.out((c & 0xf0) | LCD_RS) #output upper nibble
        self.toggleE()              #toggle LCD_E, the enable pin
        self.out(((c << 4) & 0xf0) | LCD_RS) #and then the lower nibble
        self.toggleE()              #toggle LCD_E, the enable pin
        time.sleep(0.001)           #wait until instr is finished


class EightBitIO(object):
    def __init__(self):
        self.data = 0
        
        self.setRS(0)
        self.setRW(0)
        self.out(0)                 #reset pins
        time.sleep(0.050)           #wait more than 30ms
        #send the reset sequece (3 times the same pattern)
        self.out(LCD8BITS)          #set 8 bit interface
        self.toggleE()              #toggle LCD_E, the enable pin
        time.sleep(0.005)           #wait a bit
        self.toggleE()              #toggle LCD_E, the enable pin
        time.sleep(0.005)           #wait a bit
        self.toggleE()              #toggle LCD_E, the enable pin
        time.sleep(0.005)           #wait a bit
        
        #~ self.instr(LCD2LINES)       #set 2 lines display
        self.instr(LCDCURSOROFF)    #hide cursor
        self.instr(LCDCLEAR)        #clear display

    def setRW(self, state):
        self.p.setAutoFeed(state)
    
    def setRS(self, state):
        self.p.setInitOut(state)
        
    def toggleE(self):
        """toggle enable pin"""
        self.p.setDataStrobe(1)     #toggle LCD_E, the enable pin
        #~ time.sleep(0.001)
        self.p.setDataStrobe(0)     #back to inactive position
        #~ time.sleep(0.001)

    def out(self, data):
        """set data to LCD port"""
        self.data = data
        self.p.setData(self.data)

    def instr(self, cmd):
        """send instruction byte to LCD"""
        self.setRS(0)
        self.setRW(0)
        self.out(cmd)
        self.toggleE()              #toggle LCD_E, the enable pin
        time.sleep(0.005)           #wait until instr is finished

    def putc(self, c):
        """send a data byte to the LCD"""
        self.setRS(1)
        self.setRW(0)
        self.out(ord(c))
        self.toggleE()              #toggle LCD_E, the enable pin
        time.sleep(0.001)           #wait until instr is finished


#~ class HD44780(FourBitIO):
class HD44780(EightBitIO):
    def __init__(self):
        self.p = parallel.Parallel()
        super(HD44780, self).__init__()
        
    def write(self, str):
        """write a string to the LCD"""
        for c in str:
            self.putc(c)            #write each character

    def downloadFont(self, fontdata):
        """Set the memory pointer and download a font"""
        self.instr(LCDCGADRSET);
        self.write(fontdata)
        self.instr(LCDLINE1)        #just in case, set cursor to a visible pos

if __name__ == '__main__':
    lcd = HD44780()
    lcd.write("Hello World")
    lcd.instr(LCDLINE2)
    lcd.write("from Python")
##    for c in map(chr,range(256)):
##        lcd.instr(LCDLINE1)
##        lcd.write(c)

    