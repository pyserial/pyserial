from typing import Optional
from .serialutil import _Serial, _Cancellable, _OutputFlowControl, _OutWaiting

class Serial(_Serial, _Cancellable, _OutputFlowControl, _OutWaiting):
    def set_buffer_size(
        self, rx_size: int = 4096, tx_size: Optional[int] = None
    ) -> None: ...
