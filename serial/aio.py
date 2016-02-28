import asyncio
import os
import serial


__all__ = ["AsyncSerial"]


class AsyncSerialBase:
    def __init__(self, *args, loop=None, **kwargs):
        self.ser = serial.serial_for_url(*args, **kwargs)

        if loop is None:
            loop = asyncio.get_event_loop()
        self._loop = loop

        self.read_future = None
        self.write_future = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    async def read_exactly(self, n):
        data = bytesarray()
        while len(data) < n:
            remaining = n - len(data)
            data += await self.read(remaining)
        return data

    async def write_exactly(self, data):
        while data:
            res = await self.write(data)
            data = data[res:]


if os.name != "nt":
    class AsyncSerial(AsyncSerialBase):
        def fileno(self):
            return self.ser.fd

        def _read_ready(self, n):
            self._loop.remove_reader(self.fileno())
            if not self.read_future.cancelled():
                try:
                    res = os.read(self.fileno(), n)
                except Exception as exc:
                    self.read_future.set_exception(exc)
                else:
                    self.read_future.set_result(res)
            self.read_future = None

        def read(self, n):
            assert self.read_future is None or self.read_future.cancelled()
            future = asyncio.Future(loop=self._loop)

            if n == 0:
                future.set_result(b"")
            else:
                try:
                    res = os.read(self.fileno(), n)
                except Exception as exc:
                    future.set_exception(exc)
                else:
                    if res:
                        future.set_result(res)
                    else:
                        self.read_future = future
                        self._loop.add_reader(self.fileno(),
                                              self._read_ready, n)

            return future

        def _write_ready(self, data):
            self._loop.remove_writer(self.fileno())
            if not self.write_future.cancelled():
                try:
                    res = os.write(self.fileno(), data)
                except Exception as exc:
                    self.write_future.set_exception(exc)
                else:
                    self.write_future.set_result(res)
            self.write_future = None

        def write(self, data):
            assert self.write_future is None or self.write_future.cancelled()
            future = asyncio.Future(loop=self._loop)

            if len(data) == 0:
                future.set_result(0)
            else:
                try:
                    res = os.write(self.fileno(), data)
                except BlockingIOError:
                    self.write_future = future
                    self._loop.add_writer(self.fileno(),
                                          self._write_ready, data)
                except Exception as exc:
                    future.set_exception(exc)
                else:
                    future.set_result(res)

            return future

        def close(self):
            if self.read_future is not None:
                self._loop.remove_reader(self.fileno())
            if self.write_future is not None:
                self._loop.remove_writer(self.fileno())
            self.ser.close()

else:
    class AsyncSerial(AsyncSerialBase):
        """Requires ProactorEventLoop"""
        def fileno(self):
            return self.ser._port_handle

        def read(self, n):
            return self._loop._proactor.recv(self.fileno(), n)

        def write(self, data):
            return self._loop._proactor.send(self.fileno(), data)

        def close(self):
            self.ser.close()
