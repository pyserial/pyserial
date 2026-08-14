import sys

import pytest

import serial.tools.list_ports as list_ports
from serial.tools.list_ports_common import ListPortInfo


class ComportsMock:
    """Mock `comports()`, but allow tests to customize the ports that were "found"."""

    def __init__(self):
        self.call_count = 0
        self.include_links_args = []
        self.ports = []

    def __call__(self, *args, **kwargs):
        self.call_count += 1
        if args:
            self.include_links_args.append(args[0])
        else:
            assert kwargs
            self.include_links_args.append(kwargs["include_links"])
        return self.ports

    def set_ports(self, ports):
        # Tests call this function to customize the ports that were "found".
        self.ports = ports


@pytest.fixture(autouse=True)
def comports(monkeypatch):
    """Monkeypatch serial.tools.list_ports.comports."""

    comports_mock = ComportsMock()
    monkeypatch.setattr(list_ports, "comports", comports_mock)
    yield comports_mock

    # `comports()` must be called a maximum of one time.
    assert comports_mock.call_count in (0, 1)


@pytest.fixture(autouse=True)
def set_cli_args(monkeypatch):
    """Monkeypatch the CLI arguments. By default, there are no CLI args."""

    def setter(*args):
        sys_argv = [""]
        sys_argv.extend([arg for arg in args if arg is not None])
        monkeypatch.setattr("sys.argv", sys_argv)

    monkeypatch.setattr(sys, "argv", [""])
    yield setter


@pytest.mark.parametrize("quiet_arg", ("-q", "--quiet", None))
def test_quiet_arg(set_cli_args, capsys, quiet_arg):
    """Test behavior of the `--quiet` option."""

    set_cli_args(quiet_arg)

    list_ports.main()

    stdout, stderr = capsys.readouterr()
    assert stdout == ""
    if quiet_arg:
        assert stderr == ""
    else:
        assert "no ports found" in stderr.strip().lower()


@pytest.mark.parametrize("include_links_arg", ("-s", "--include-links", None))
@pytest.mark.parametrize("regex_pattern", (None, "."))
def test_include_links_arg(set_cli_args, comports, include_links_arg, regex_pattern):
    """Test behavior of the `--include-links` option."""

    set_cli_args(regex_pattern, include_links_arg)
    list_ports.main()
    assert comports.include_links_args == [bool(include_links_arg)]


def get_some_ports():
    """Generate some unique `ListPortInfo` instances."""

    ports = []
    for i in range(1, 4):
        port = ListPortInfo(f"port{i}{i}{i}", skip_link_detection=True)
        port.description = f"desc{i}{i}{i}"
        port.hwid = f"hwid{i}{i}{i}"
        ports.append(port)
    return ports


@pytest.mark.parametrize("verbose_arg", ("-v", "--verbose", None))
def test_verbose_arg(set_cli_args, capsys, comports, verbose_arg):
    """Test behavior of the `--verbose` option."""

    # Setup
    set_cli_args(verbose_arg)
    ports = get_some_ports()
    comports.set_ports(ports)

    # Act
    list_ports.main()

    # Verify
    stdout, stderr = capsys.readouterr()
    lines = [line.strip() for line in stdout.strip().splitlines()]
    for port in ports:
        assert port.device in lines
        if verbose_arg is not None:
            assert f"desc: {port.description}" in lines
            assert f"hwid: {port.hwid}" in lines

    assert stderr.lower().strip() == f"{len(ports)} ports found"


@pytest.mark.parametrize("only_one_arg", ("-1", "--only-one"))
@pytest.mark.parametrize("port_count", (0, 1, 2))
def test_only_one_arg(set_cli_args, capsys, comports, only_one_arg, port_count):
    """Test behavior of the `--only-one` option."""

    # Setup
    set_cli_args(only_one_arg)
    ports = get_some_ports()[:port_count]
    comports.set_ports(ports)

    # Act and verify
    if len(ports) == 1:
        list_ports.main()
    else:
        with pytest.raises(SystemExit) as error:
            list_ports.main()
        assert error.value.code == 1

        stdout, stderr = capsys.readouterr()
        assert stdout == ""
        expected_message = f"error: {len(ports) or 'no'} serial ports"
        assert stderr.lower().strip().startswith(expected_message)


@pytest.mark.parametrize("pattern", ("port.2.", "desc.2.", "hwid.2."))
@pytest.mark.parametrize("quiet_arg", ("--quiet", None))
def test_regex_filtering(set_cli_args, capsys, comports, pattern, quiet_arg):
    """Test behavior of the regex argument.

    *pattern* confirms that the device, description, and hwid values are each searched.
    """

    # Setup
    set_cli_args(pattern, quiet_arg)
    ports = get_some_ports()
    comports.set_ports(ports)

    # Act
    list_ports.main()

    # Verify
    stdout, stderr = capsys.readouterr()
    assert "2" in stdout
    if not quiet_arg:
        assert f"filtered list with regexp: {pattern!r}" in stderr.lower()
        assert "1 ports found" in stderr.lower()


def test_n_arg(set_cli_args, capsys, comports):
    """Test behavior of the `-n` option."""

    set_cli_args("-n", "1")
    ports = get_some_ports()
    comports.set_ports(ports)

    list_ports.main()

    stdout, _ = capsys.readouterr()
    assert "port111" in stdout


@pytest.mark.parametrize("n_arg", (0, sys.maxsize))
def test_n_arg_out_of_range(set_cli_args, capsys, comports, n_arg):
    """Test that an out-of-range `-n` value eliminates all results."""

    set_cli_args("-n", str(n_arg))
    ports = get_some_ports()
    comports.set_ports(ports)

    list_ports.main()

    stdout, stderr = capsys.readouterr()
    assert stdout == ""
    assert stderr.strip().lower() == "no ports found"
