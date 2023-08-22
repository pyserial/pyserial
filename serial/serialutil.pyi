import io
from types import TracebackType
from typing import (
    Callable,
    ClassVar,
    ContextManager,
    Iterable,
    Iterator,
    Literal,
    MutableSequence,
    Optional,
    Protocol,
    Type,
    TypeVar,
    TypedDict,
    Union,
)

def iterbytes(b: bytes) -> Iterator[bytes]: ...

_ToBytes = Union[Iterable[int], bytes, bytearray, memoryview]

def to_bytes(seq: _ToBytes) -> bytes: ...

XON: bytes
XOFF: bytes
CR: bytes
LF: bytes

_Parity = Literal["N", "E", "O", "M", "S"]
PARITY_NONE: Literal["N"]
PARITY_EVEN: Literal["E"]
PARITY_ODD: Literal["O"]
PARITY_MARK: Literal["M"]
PARITY_SPACE: Literal["S"]

_Stopbits = Union[Literal[1, 2], float]
STOPBITS_ONE: Literal[1]
STOPBITS_ONE_POINT_FIVE: float  # Literal[1.5]
STOPBITS_TWO: Literal[2]

_Bytesize = Literal[5, 6, 7, 8]
FIVEBITS: Literal[5]
SIXBITS: Literal[6]
SEVENBITS: Literal[7]
EIGHTBITS: Literal[8]

class _ParityNames(TypedDict):
    N: Literal["None"]
    E: Literal["Even"]
    O: Literal["Odd"]
    M: Literal["Mark"]
    S: Literal["Space"]

PARITY_NAMES: _ParityNames

class SerialException(IOError):
    pass

class SerialTimeoutException(SerialException):
    pass

class PortNotOpenError(SerialException):
    pass

# None: wait forever
# 0: non-blocking
# float: seconds
_TimeoutDuration = Optional[Union[float, int]]

class Timeout:
    TIME: ClassVar[Callable[[], float]]  # time.monotonic
    def __init__(self, duration: _TimeoutDuration) -> None: ...
    def expired(self) -> bool: ...
    def time_left(self) -> _TimeoutDuration: ...
    # Seems this form doesn't support `None` for infinite
    def restart(self, duration: float) -> None: ...

_Baudrate = Literal[
    50,
    75,
    110,
    134,
    150,
    200,
    300,
    600,
    1200,
    1800,
    2400,
    4800,
    9600,
    19200,
    38400,
    57600,
    115200,
    230400,
    460800,
    500000,
    576000,
    921600,
    1000000,
    1152000,
    1500000,
    2000000,
    2500000,
    3000000,
    3500000,
    4000000,
]

# Corresponding to SerialBase._SAVED_SETTINGS
class _SerialSettings(TypedDict):
    baudrate: _Baudrate
    bytesize: _Bytesize
    parity: _Parity
    stopbits: _Stopbits
    xonxoff: bool
    dsrdtr: Optional[bool]
    rtscts: bool
    timeout: _TimeoutDuration
    write_timeout: _TimeoutDuration
    inter_byte_timeout: _TimeoutDuration

_S = TypeVar("_S", bound="SerialBase")

# Deprecated functions are omitted here!
class SerialBase(io.RawIOBase, ContextManager):
    BAUDRATES: ClassVar[tuple[int, ...]]
    BYTESIZES: ClassVar[tuple[int, ...]]
    PARITIES: ClassVar[tuple[_Parity, ...]]
    STOPBITS: ClassVar[tuple[Literal[1, 2] | float, ...]]  # 1, 1.5, 2
    def __init__(
        self,
        port: Optional[str] = None,
        baudrate: _Baudrate = 9600,
        bytesize: _Bytesize = EIGHTBITS,
        parity: _Parity = PARITY_NONE,
        stopbits: _Stopbits = STOPBITS_ONE,
        timeout: _TimeoutDuration = None,
        xonxoff: bool = False,
        rtscts: bool = False,
        write_timeout: _TimeoutDuration = None,
        dsrdtr: Optional[bool] = False,
        inter_byte_timeout: _TimeoutDuration = None,
        exclusive: Optional[bool] = None,
    ) -> None: ...
    @property
    def port(self) -> Optional[str]: ...
    @port.setter
    def port(self, port: Optional[str]) -> None: ...
    @property
    def baudrate(self) -> _Baudrate: ...
    @baudrate.setter
    def baudrate(self, baudrate: _Baudrate) -> None: ...
    @property
    def bytesize(self) -> _Bytesize: ...
    @bytesize.setter
    def bytesize(self, bytesize: _Bytesize) -> None: ...
    @property
    def exclusive(self) -> Optional[bool]: ...
    @exclusive.setter
    def exclusive(self, exclusive: Optional[bool]) -> None: ...
    @property
    def parity(self) -> _Parity: ...
    @parity.setter
    def parity(self, parity: _Parity) -> None: ...
    @property
    def stopbits(self) -> _Stopbits: ...
    @stopbits.setter
    def stopbits(self, stopbits: _Stopbits) -> None: ...
    @property
    def timeout(self) -> _TimeoutDuration: ...
    @timeout.setter
    def timeout(self, timeout: _TimeoutDuration) -> None: ...
    @property
    def write_timeout(self) -> _TimeoutDuration: ...
    @write_timeout.setter
    def write_timeout(self, timeout: _TimeoutDuration) -> None: ...
    @property
    def inter_byte_timeout(self) -> _TimeoutDuration: ...
    @inter_byte_timeout.setter
    def inter_byte_timeout(self, ic_timeout: _TimeoutDuration) -> None: ...
    @property
    def xonxoff(self) -> bool: ...
    @xonxoff.setter
    def xonxoff(self, xonxoff: bool) -> None: ...
    @property
    def rtscts(self) -> bool: ...
    @rtscts.setter
    def rtscts(self, rtscts: bool) -> None: ...
    @property
    def dsrdtr(self) -> bool: ...
    # Is it even meaningful for a property setter to have a default value? I doubt it.
    @dsrdtr.setter
    def dsrdtr(self, dsrdtr: Optional[bool] = None) -> None: ...
    @property
    def rts(self) -> Optional[bool]: ...
    @rts.setter
    def rts(self, value: Optional[bool]) -> None: ...
    @property
    def dtr(self) -> Optional[bool]: ...
    @dtr.setter
    def dtr(self, value: Optional[bool]) -> None: ...
    @property
    def break_condition(self) -> bool: ...
    @break_condition.setter
    def break_condition(self, value: bool) -> None: ...
    @property
    def rs485_mode(self) -> Optional[bool]: ...
    @rs485_mode.setter
    def rs485_mode(self, rs485_settings: Optional[bool]) -> None: ...
    def get_settings(self) -> _SerialSettings: ...
    def apply_settings(self, d: _SerialSettings) -> None: ...
    def readable(self) -> Literal[True]: ...
    def writable(self) -> Literal[True]: ...
    def seekable(self) -> Literal[False]: ...
    def __enter__(self: _S) -> _S: ...
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None: ...
    def send_break(self, duration: float = 0.25) -> None: ...
    # additional functionality
    # Does self.read ever return None?
    def read_all(self) -> Optional[bytes]: ...
    def read_until(self, expected: bytes = LF, size: Optional[int] = None) -> bytes: ...
    def iread_until(
        self, expected: bytes = LF, size: Optional[int] = None
    ) -> Iterator[bytes]: ...

class _Serial(SerialBase):
    def open(self) -> None: ...
    def close(self) -> None: ...
    def read(self, size: int = 1) -> bytes: ...
    def flush(self) -> None: ...
    @property
    def in_waiting(self) -> int: ...
    def reset_input_buffer(self) -> None: ...
    def reset_output_buffer(self) -> None: ...
    @property
    def cts(self) -> bool: ...
    @property
    def dsr(self) -> bool: ...
    @property
    def ri(self) -> bool: ...
    @property
    def cd(self) -> bool: ...

class _Cancellable(Protocol):
    def cancel_read(self) -> None: ...
    def cancel_write(self) -> None: ...

class _OutputFlowControl(Protocol):
    def set_output_flow_control(self, enable: bool = True) -> None: ...

class _OutWaiting(Protocol):
    @property
    def out_waiting(self) -> int: ...
