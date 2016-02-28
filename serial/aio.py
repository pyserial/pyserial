import asyncio
import os
import serial


__all__ = ["AsyncSerial"]


class _ExactIO:
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
    class AsyncSerial(_ExactIO):
        def __init__(self, *args, loop=None, **kwargs):
            self.ser = serial.serial_for_url(*args, **kwargs)

            if loop is None:
                loop = asyncio.get_event_loop()
            self._loop = loop

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.close()

        def fileno(self):
            return self.ser.fd

        def _read_ready(self, future, n):
            self._loop.remove_reader(self.fileno())
            if not future.cancelled():
                try:
                    res = os.read(self.fileno(), n)
                except Exception as exc:
                    future.set_exception(exc)
                else:
                    future.set_result(res)

        async def read(self, n):
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
                        self._loop.add_reader(self.fileno(),
                                              self._read_ready,
                                              future, n)

            return await future

        def _write_ready(self, future, data):
            self._loop.remove_writer(self.fileno())
            if not future.cancelled():
                try:
                    res = os.write(self.fileno(), data)
                except Exception as exc:
                    future.set_exception(exc)
                else:
                    self._loop.remove_writer(self.fileno())
                    future.set_result(written + res)

        async def write(self, data):
            future = asyncio.Future(loop=self._loop)

            if len(data) == 0:
                future.set_result(0)
            else:
                try:
                    res = os.write(self.fileno(), data)
                except BlockingIOError:
                    self._loop.add_writer(self.fileno(),
                                          self._write_ready,
                                          future, data)
                except Exception as exc:
                    future.set_exception(exc)
                else:
                    future.set_result(res)

            return await future

        def close(self):
            self._loop.remove_reader(self.fileno())
            self._loop.remove_writer(self.fileno())
            self.ser.close()

else:
    class AsyncSerial(_ExactIO):
        raise NotImplementedError
