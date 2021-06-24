from typing import Any, List
import sys

from .serialutil import *

protocol_handler_packages: List[str]

__version__: str
VERSION: str

if sys.platform == "cli":
    from .serialcli import Serial
elif sys.platform == "win32":
    from .serialwin32 import Serial
elif sys.platform == "linux" or sys.platform == "cygwin" or sys.platform == "darwin":
    from .serialposix import Serial, PosixPollSerial, VTIMESerial
else:
    # For `os.name == 'java'`
    from .serialutil import _Serial as Serial

def serial_for_url(
    url: str, *args: Any, do_not_open: bool = False, **kwargs: Any
) -> None: ...
