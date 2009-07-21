class BitaccessMeta(type):
    """meta class that adds bit access properties to a
    parallel port implementation"""

    def __new__(self, classname, bases, classdict):
        klass = type.__new__(self, classname, bases, classdict)
        # status lines
        klass.paperOut = property(klass.getInPaperOut, None, "Read the PaperOut signal")
        # control lines
        klass.dataStrobe = property(None, klass.setDataStrobe, "Set the DataStrobe signal")
        # XXX ... other bits
        # data bits
        for bit in range(8):
            mask = (1<<bit)
            def getter(self, mask=mask):
                return (self.getData() & mask) != 0
            def setter(self, b, mask=mask):
                if b:
                    self.setData(self.getData() | mask)
                else:
                    self.setData(self.getData() & ~mask)
            setattr(klass, "D%d" % bit, property(getter, setter, "Access databit %d" % bit))
        # nibbles
        for name, shift, width in [('D0_D3', 0, 4), ('D4_D7', 4, 4)]:
            mask = (1<<width) - 1
            def getter(self, shift=shift, mask=mask):
                return (self.getData() >> shift) & mask
            def setter(self, b, shift=shift, mask=mask):
                self.setData((self.getData() & ~(mask<<shift)) | ((b&mask) << shift))
            setattr(klass, name, property(getter, setter, "Access to %s" % name))
        return klass

class VirtualParallelPort:
    """provides a virtual parallel port implementation, useful
    for tests and simulations without real hardware"""

    __metaclass__ = BitaccessMeta

    def __init__(self, port=None):
        self._data = 0

    def setData(self, value):
        self._data = value

    def getData(self):
        return self._data

    # inputs return dummy value
    def getInPaperOut(self): return self._dummy
    # ...
    # outputs just store a tuple with (action, value) pair
    def setDataStrobe(self, value): self._last = ('setDataStrobe', value)
    # ...

# testing
if __name__ == '__main__':
    import unittest, sys

    class TestBitaccess(unittest.TestCase):
        """Tests a port with no timeout"""
        def setUp(self):
            self.p = VirtualParallelPort()

        def testDatabits(self):
            """bit by bit D0..D7"""
            p = self.p
            p.D0 = p.D2  = p.D4 = p.D6 = 1
            self.failUnlessEqual(p._data, 0x55)
            self.failUnlessEqual(
                [p.D7, p.D6, p.D5, p.D4, p.D3, p.D2, p.D1, p.D0],
                [0, 1, 0, 1, 0, 1, 0, 1]
            )
            p._data <<= 1
            self.failUnlessEqual(
                [p.D7, p.D6, p.D5, p.D4, p.D3, p.D2, p.D1, p.D0],
                [1, 0, 1, 0, 1, 0, 1, 0]
            )

        def testDatabitsGroups(self):
            """nibbles D0..D7"""
            p = self.p
            p.D0_D3 = 14
            self.failUnlessEqual(p._data, 0x0e)
            p.D0_D3 = 0
            p.D4_D7 = 13
            self.failUnlessEqual(p._data, 0xd0)
            p.D0_D3 = p.D4_D7 = 0xa
            self.failUnlessEqual(p._data, 0xaa)
            # test bit patterns
            for x in range(256):
                # test getting
                p._data = x
                self.failUnlessEqual((p.D4_D7, p.D0_D3), (((x>>4) & 0xf), (x & 0xf)))
                # test setting
                p._data = 0
                (p.D4_D7, p.D0_D3) = (((x>>4) & 0xf), (x & 0xf))
                self.failUnlessEqual(p._data, x)

        def testStatusbits(self):
            """bit by bit status lines"""
            # read the property:
            self.p._dummy = 0
            self.failUnlessEqual(self.p.paperOut, 0)

            self.p._dummy = 1
            self.failUnlessEqual(self.p.paperOut, 1)

            # read only, must not be writable:
            self.failUnlessRaises(AttributeError, setattr, self.p, 'paperOut', 1)

        def testControlbits(self):
            """bit by bit control lines"""
            self.p.dataStrobe = 0
            self.failUnlessEqual(self.p._last, ('setDataStrobe', 0))
            self.p.dataStrobe = 1
            self.failUnlessEqual(self.p._last, ('setDataStrobe', 1))

            # write only, must not be writable:
            self.failUnlessRaises(AttributeError, getattr, self.p, 'dataStrobe')

    sys.argv.append('-v')
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()

