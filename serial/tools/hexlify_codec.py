#! python
#
# This is a codec to create and decode hexdumps with spaces between characters. used by miniterm.
#
# This file is part of pySerial. https://github.com/pyserial/pyserial
# (C) 2011 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Python 'hex' Codec - 2-digit hex with spaces content transfer encoding.
"""

import codecs
import serial

HEXDIGITS = '0123456789ABCDEF'

### Codec APIs


def hex_encode(input, errors='strict'):
    return (serial.to_bytes([int(h, 16) for h in input.split()]), len(input))


def hex_decode(input, errors='strict'):
    return (''.join('{:02X} '.format(b) for b in input), len(input))


class Codec(codecs.Codec):
    def encode(self, input, errors='strict'):
        return serial.to_bytes([int(h, 16) for h in input.split()])

    def decode(self, input, errors='strict'):
        return ''.join('{:02X} '.format(b) for b in input)


class IncrementalEncoder(codecs.IncrementalEncoder):

    def __init__(self, errors='strict'):
        self.errors = errors
        self.state = 0

    def reset(self):
        self.state = 0

    def getstate(self):
        return self.state

    def setstate(self, state):
        self.state = state

    def encode(self, input, final=False):
        state = self.state
        encoded = []
        for c in input.upper():
            if c in HEXDIGITS:
                z = HEXDIGITS.index(c)
                if state:
                    encoded.append(z + (state & 0xf0))
                    state = 0
                else:
                    state = 0x100 + (z << 4)
            elif c == ' ':      # allow spaces to separate values
                if state and self.errors == 'strict':
                    raise UnicodeError('odd number of hex digits')
                state = 0
            else:
                if self.errors == 'strict':
                    raise UnicodeError('non-hex digit found: %r' % c)
        self.state = state
        return serial.to_bytes(encoded)


class IncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, input, final=False):
        return ''.join('{:02X} '.format(b) for b in input)


class StreamWriter(Codec, codecs.StreamWriter):
    pass


class StreamReader(Codec, codecs.StreamReader):
    pass


### encodings module API
def getregentry():
    return codecs.CodecInfo(
        name='hexlify',
        encode=hex_encode,
        decode=hex_decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamwriter=StreamWriter,
        streamreader=StreamReader,
        _is_text_encoding=True,
    )
