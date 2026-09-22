"""Reader timeout and real local socket transport regression checks."""
import queue
import socket
import unittest

import serial
from serial.threaded import LineReader, Protocol, ReaderThread


class TestReaderTimeout(unittest.TestCase):
    def test_short_timeout_is_preserved_on_socket_transport(self):
        lines = queue.Queue()

        class Lines(LineReader):
            def handle_line(self, line):
                lines.put(line)

        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            listener.listen(1)
            listener.settimeout(2)
            port = listener.getsockname()[1]
            device = serial.serial_for_url('socket://127.0.0.1:{}'.format(port), timeout=0.05)
            peer, _ = listener.accept()
            reader = ReaderThread(device, Lines)
            try:
                with reader:
                    self.assertEqual(device.timeout, 0.05)
                    peer.sendall(b'hello\r\n')
                    self.assertEqual(lines.get(timeout=2), 'hello')
                self.assertFalse(reader.is_alive())
            finally:
                device.close()
                peer.close()

    def test_fallback_remains_bounded_and_blocking(self):
        class Device:
            is_open = True

        class StopAfterConnect(Protocol):
            def connection_made(self, transport):
                transport.alive = False

        for initial, expected in [(None, 1), (0, 1), (5, 1), (1, 1), (0.2, 0.2)]:
            with self.subTest(timeout=initial):
                device = Device()
                device.timeout = initial
                ReaderThread(device, StopAfterConnect).run()
                self.assertEqual(device.timeout, expected)

    def test_cancel_read_keeps_configured_timeout(self):
        class Device:
            is_open = True

            def cancel_read(self):
                pass

        class StopAfterConnect(Protocol):
            def connection_made(self, transport):
                transport.alive = False

        for initial in [None, 0, 0.2, 1, 5]:
            with self.subTest(timeout=initial):
                device = Device()
                device.timeout = initial
                ReaderThread(device, StopAfterConnect).run()
                self.assertEqual(device.timeout, initial)
