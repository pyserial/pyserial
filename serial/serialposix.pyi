import sys
from typing import ClassVar, Literal

from .serialutil import (
    _Serial,
    _Baudrate,
    _Cancellable,
    _OutputFlowControl,
    _OutWaiting,
)

class PlatformSpecificBase:
    BAUDRATE_CONSTANTS: dict[_Baudrate, int]

    # TODO
    def set_low_latency_mode(self, low_latency_settings: bool) -> None: ...

if sys.platform == "linux":
    CMSPAR: Literal[0o10000000000]

    TCGETS2: Literal[0x802C542A]
    TCSETS2: Literal[0x402C542B]
    BOTHER: Literal[0o010000]

    TIOCGRS485: Literal[0x542E]
    TIOCSRS485: Literal[0x542F]
    SER_RS485_ENABLED: Literal[0b00000001]
    SER_RS485_RTS_ON_SEND: Literal[0b00000010]
    SER_RS485_RTS_AFTER_SEND: Literal[0b00000100]
    SER_RS485_RX_DURING_TX: Literal[0b00010000]
    class PlatformSpecific(PlatformSpecificBase):
        pass

elif sys.platform == "darwin":
    IOSSIOSPEED: Literal[0x80045402]
    class PlatformSpecific(PlatformSpecificBase):
        osx_version: ClassVar[list[str]]
        TIOCSBRK: Literal[0x2000747B]
        TIOCCBRK: Literal[0x2000747A]

else:
    class PlatformSpecific(PlatformSpecificBase):
        pass

TIOCMGET: int
TIOCMBIS: int
TIOCMBIC: int
TIOCMSET: int
TIOCM_DTR: int
TIOCM_RTS: int
TIOCM_CTS: int
TIOCM_CAR: int
TIOCM_RNG: int
TIOCM_DSR: int
TIOCM_CD: int
TIOCM_RI: int
TIOCINQ: int
TIOCOUTQ: int

TIOCM_zero_str: bytes
TIOCM_RTS_str: bytes
TIOCM_DTR_str: bytes

TIOCSBRK: int
TIOCCBRK: int

class Serial(_Serial, PlatformSpecific, _Cancellable, _OutputFlowControl, _OutWaiting):
    def fileno(self) -> int: ...
    def set_input_flow_control(self, enable: bool = True) -> None: ...

class PosixPollSerial(Serial):
    pass

class VTIMESerial(Serial):
    pass
