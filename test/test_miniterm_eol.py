"""Terminal newline handling for miniterm's opt-in raw EOL mode."""
import os
import subprocess
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import Mock


def _run_case(name):
    # Importing miniterm registers the hexlify codec globally. Keep that side
    # effect out of the pytest process so the codec teardown tests stay isolated.
    subprocess.check_call([sys.executable, __file__, name])


def _case_pty(miniterm):
    import pty
    import termios

    master, slave = pty.openpty()
    original = termios.tcgetattr(slave)
    try:
        cooked = termios.tcgetattr(slave)
        cooked[0] |= termios.ICRNL
        termios.tcsetattr(slave, termios.TCSANOW, cooked)
        console = miniterm.Console.__new__(miniterm.Console)
        console.fd = slave
        console.old = termios.tcgetattr(slave)
        console.miniterm = SimpleNamespace(eol='raw')
        console.setup()
        os.write(master, b'\r\n')
        assert os.read(slave, 1) + os.read(slave, 1) == b'\r\n'
        console.miniterm.eol = 'lf'
        console.setup()
        os.write(master, b'\r\n')
        assert os.read(slave, 1) + os.read(slave, 1) == b'\n\n'
    finally:
        termios.tcsetattr(slave, termios.TCSANOW, original)
        os.close(master)
        os.close(slave)


def _case_transform(miniterm):
    terminal = miniterm.Miniterm.__new__(miniterm.Miniterm)
    terminal.eol = 'raw'
    terminal.filters = []
    terminal.update_transformations()
    assert terminal.tx_transformations[0].tx('\r\n') == '\r\n'


def _case_menu(miniterm):
    terminal = miniterm.Miniterm.__new__(miniterm.Miniterm)
    terminal.eol = 'lf'
    terminal.filters = []
    terminal.menu_character = '\x14'
    terminal.exit_character = '\x1d'
    terminal.console = SimpleNamespace(setup=Mock())
    terminal.handle_menu_key('\x0c')
    assert terminal.eol == 'raw'
    terminal.console.setup.assert_called_once_with()


class TestRawEol(unittest.TestCase):
    @unittest.skipUnless(os.name == 'posix', 'requires a POSIX terminal')
    def test_console_keeps_cr_distinct_from_lf_in_raw_eol_mode(self):
        _run_case('pty')

    def test_raw_eol_transform_preserves_both_newline_characters(self):
        _run_case('transform')

    def test_menu_switch_reconfigures_console_input(self):
        _run_case('menu')


if __name__ == '__main__' and len(sys.argv) == 2:
    from serial.tools import miniterm

    {'pty': _case_pty, 'transform': _case_transform, 'menu': _case_menu}[sys.argv[1]](miniterm)
