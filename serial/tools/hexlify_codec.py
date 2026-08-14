# This is a codec to create and decode hexdumps with spaces between characters.
#
# This file is part of pySerial. https://github.com/pyserial/pyserial
# (C) 2015-2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Python 'hexlify' Codec - 2-digit hex with spaces content transfer encoding.
The built-in 'hex_codec' is similar, but encodes and decodes to bytes
and doesn't return spaces between pairs of hexadecimal digits.

Encode and decode may be a bit misleading at first sight...

The str representation is a hex dump: e.g. "40 41"
The "encoded" bytes representation of this is the binary form, e.g. b"@A"

Thus, decoding is binary to text and thus converting binary data to hex dump.

"""

import codecs

HEXDIGITS = "0123456789ABCDEF"


# Codec APIs


def hex_encode(data: str, errors: str = "strict") -> tuple[bytes, int]:
    """'40 41 42' -> b'@AB'"""
    return bytes.fromhex(data), len(data)


def hex_decode(data: bytes | memoryview, errors: str = "strict") -> tuple[str, int]:
    """b'@AB' -> '40 41 42'"""
    return data.hex(sep=" ").upper() + " ", len(data)


class Codec(codecs.Codec):
    def encode(self, data: str, errors: str = "strict") -> tuple[bytes, int]:
        """'40 41 42' -> b'@AB'"""
        return bytes.fromhex(data), len(data)

    def decode(self, data: bytes, errors: str = "strict") -> tuple[str, int]:
        """b'@AB' -> '40 41 42'"""
        return data.hex(sep=" ").upper() + " ", len(data)


class IncrementalEncoder(codecs.IncrementalEncoder):
    """Incremental hex encoder"""

    def __init__(self, errors: str = "strict") -> None:
        self.errors = errors
        self.state = 0

    def reset(self) -> None:
        self.state = 0

    def getstate(self) -> int:
        return self.state

    def setstate(self, state: int) -> None:
        self.state = state

    def encode(self, data: str, final: bool = False) -> bytes:
        """\
        Incremental encode, keep track of digits and emit a byte when a pair
        of hex digits is found. The space is optional unless the error
        handling is defined to be 'strict'.
        """
        state = self.getstate()
        encoded = []
        for c in data.upper():
            if c in HEXDIGITS:
                z = HEXDIGITS.index(c)
                if state:
                    encoded.append(z + (state & 0xF0))
                    state = 0
                else:
                    state = 0x100 + (z << 4)
            elif c == " ":  # allow spaces to separate values
                if state and self.errors == "strict":
                    raise UnicodeError("odd number of hex digits")
                state = 0
            else:
                if self.errors == "strict":
                    raise UnicodeError(f"non-hex digit found: {c!r}")
        self.setstate(state)
        return bytes(encoded)


class IncrementalDecoder(codecs.IncrementalDecoder):
    """Incremental decoder"""

    def decode(self, data: bytes, final: bool = False):
        return data.hex(sep=" ").upper() + " "


class StreamWriter(Codec, codecs.StreamWriter):
    """Combination of hexlify codec and StreamWriter"""


class StreamReader(Codec, codecs.StreamReader):
    """Combination of hexlify codec and StreamReader"""


def getregentry() -> codecs.CodecInfo:
    """encodings module API"""
    return codecs.CodecInfo(
        name="hexlify",
        encode=hex_encode,
        decode=hex_decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamwriter=StreamWriter,
        streamreader=StreamReader,
    )
