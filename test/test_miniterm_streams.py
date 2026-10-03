"""Tests for miniterm's process-global console stream handling."""

import subprocess
import sys
import unittest


class TestConsoleStreams(unittest.TestCase):
    def run_stream_restoration(self, expect_restoration):
        script = r'''
import io
import sys
from unittest import mock
from serial.tools.miniterm import ConsoleBase

original_stdout = io.StringIO()
original_stderr = io.StringIO()
console_stdout = io.StringIO()
console_stderr = io.StringIO()
console = object.__new__(ConsoleBase)
console._saved_stdout = original_stdout
console._saved_stderr = original_stderr
console._patched_stdout = console_stdout
console._patched_stderr = console_stderr

if EXPECT_RESTORATION:
    expected_stdout, expected_stderr = original_stdout, original_stderr
else:
    expected_stdout, expected_stderr = io.StringIO(), io.StringIO()

with mock.patch('serial.tools.miniterm.sys.stdout', console_stdout if EXPECT_RESTORATION else expected_stdout), \
        mock.patch('serial.tools.miniterm.sys.stderr', console_stderr if EXPECT_RESTORATION else expected_stderr):
    console.restore()
    assert sys.stdout is expected_stdout
    assert sys.stderr is expected_stderr
'''.replace('EXPECT_RESTORATION', repr(expect_restoration))
        result = subprocess.run(
            [sys.executable, '-c', script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_restore_returns_streams_replaced_by_console(self):
        self.run_stream_restoration(True)

    def test_restore_does_not_overwrite_later_stream_replacements(self):
        self.run_stream_restoration(False)


if __name__ == '__main__':
    unittest.main()
