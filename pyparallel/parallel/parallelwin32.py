#pyparallel driver for win32
#see __init__.py
#
#(C) 2002 Chris Liechti <cliechti@gmx.net>
# this is distributed under a free software license, see license.txt
#
# thanks to Dincer Aydin dinceraydin@altavista.net for his work on the
# winioport module: www.geocities.com/dinceraydin/ the graphic below is
# borrowed form him ;-)


#    LPT1 = 0x0378 or 0x03BC
#    LPT2 = 0x0278 or 0x0378
#    LPT3 = 0x0278
#
#   Data Register (base + 0) ........ outputs
#
#     7 6 5 4 3 2 1 0
#     . . . . . . . *  D0 ........... (pin 2), 1=High, 0=Low (true)
#     . . . . . . * .  D1 ........... (pin 3), 1=High, 0=Low (true)
#     . . . . . * . .  D2 ........... (pin 4), 1=High, 0=Low (true)
#     . . . . * . . .  D3 ........... (pin 5), 1=High, 0=Low (true)
#     . . . * . . . .  D4 ........... (pin 6), 1=High, 0=Low (true)
#     . . * . . . . .  D5 ........... (pin 7), 1=High, 0=Low (true)
#     . * . . . . . .  D6 ........... (pin 8), 1=High, 0=Low (true)
#     * . . . . . . .  D7 ........... (pin 9), 1=High, 0=Low (true)
#
#   Status Register (base + 1) ...... inputs
#
#     7 6 5 4 3 2 1 0
#     . . . . . * * *  Undefined
#     . . . . * . . .  Error ........ (pin 15), high=1, low=0 (true)
#     . . . * . . . .  Selected ..... (pin 13), high=1, low=0 (true)
#     . . * . . . . .  No paper ..... (pin 12), high=1, low=0 (true)
#     . * . . . . . .  Ack .......... (pin 10), high=1, low=0 (true)
#     * . . . . . . .  Busy ......... (pin 11), high=0, low=1 (inverted)
#
#   ctrl Register (base + 2) ..... outputs
#
#     7 6 5 4 3 2 1 0
#     . . . . . . . *  Strobe ....... (pin 1),  1=low, 0=high (inverted)
#     . . . . . . * .  Auto Feed .... (pin 14), 1=low, 0=high (inverted)
#     . . . . . * . .  Initialize ... (pin 16), 1=high,0=low  (true)
#     . . . . * . . .  Select ....... (pin 17), 1=low, 0=high (inverted)
#     * * * * . . . .  Unused

LPT1 = 0
LPT2 = 1

LPT1_base = 0x0378
LPT2_base = 0x0278

import ctypes
import os
#need to patch PATH so that the DLL can be found and loaded
os.environ['PATH'] = os.environ['PATH'] + ';' + os.path.abspath(os.path.dirname(__file__))
#fake module, names of the functions are the same as in the old _pyparallel
#python extension in earlier versions of this modules
_pyparallel = ctypes.windll.simpleio
#need to initialize giveio on WinNT based systems
_pyparallel.init()


class Parallel:
    def __init__(self, port = LPT1):
        if port == LPT1:
            self.dataRegAdr = LPT1_base
        elif port == LPT2:
            self.dataRegAdr = LPT2_base
        else:
            raise ValueError("No such port available - expecting a number")
        self.statusRegAdr = self.dataRegAdr + 1
        self.ctrlRegAdr   = self.dataRegAdr + 2
        self.ctrlReg = _pyparallel.inp(self.ctrlRegAdr)

    def setData(self, value):
        _pyparallel.outp(self.dataRegAdr, value)

    # control register output functions
    def setDataStrobe(self, level):
        """data strobe bit"""
        if level:
            self.ctrlReg = self.ctrlReg & ~0x01
        else:
            self.ctrlReg = self.ctrlReg |  0x01
        _pyparallel.outp(self.ctrlRegAdr, self.ctrlReg)

    def setAutoFeed(self, level):
        """auto feed bit"""
        if level:
            self.ctrlReg = self.ctrlReg & ~0x02
        else:
            self.ctrlReg = self.ctrlReg |  0x02
        _pyparallel.outp(self.ctrlRegAdr, self.ctrlReg)

    def setInitOut(self, level):
        """initialize bit"""
        if level:
            self.ctrlReg = self.ctrlReg |  0x04
        else:
            self.ctrlReg = self.ctrlReg & ~0x04
        _pyparallel.outp(self.ctrlRegAdr, self.ctrlReg)
    
    def setSelect(self, level):
        """select bit"""
        if level:
            self.ctrlReg = self.ctrlReg & ~0x08
        else:
            self.ctrlReg = self.ctrlReg |  0x08
        _pyparallel.outp(self.ctrlRegAdr, self.ctrlReg)

    def getInError(self):
        """Error pin"""
        return _pyparallel.inp(self.statusRegAdr) & 0x08 and 1

    def getInSelected(self):
        """select pin"""
        return _pyparallel.inp(self.statusRegAdr) & 0x10 and 1

    def getInPaperOut(self):
        """paper out pin"""
        return _pyparallel.inp(self.statusRegAdr) & 0x20 and 1

    def getInAcknowledge(self):
        """Acknowledge pin"""
        return _pyparallel.inp(self.statusRegAdr) & 0x40 and 1

    def getInBusy(self):
        """input from busy pin"""
        return not (_pyparallel.inp(self.statusRegAdr) & 0x80)
