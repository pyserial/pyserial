"""Linux port discovery using simulated device and sysfs records."""
from pathlib import Path
import sys

import pytest

pytestmark = pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Linux sysfs")


@pytest.mark.parametrize("subsystem,port", [("usb-serial", "ttyUSB1"), ("usb", "ttyACM0")])
@pytest.mark.parametrize("interfaces", [1, 2])
def test_link_preserves_usb_details(fs, subsystem, port, interfaces):
    from serial.tools.list_ports_linux import comports

    dev = Path("/dev")
    sys_tty = Path("/sys/class/tty")
    fs.create_dir(dev)
    fs.create_dir(sys_tty)
    root = Path("/sys")
    usb = root / "devices" / "1-3.3"
    interface = usb / "1-3.3:1.0"
    device = interface / port if subsystem == "usb-serial" else interface
    device.mkdir(parents=True)
    (device / "subsystem").symlink_to(root / "bus" / subsystem)
    tty = sys_tty / port
    tty.mkdir()
    (tty / "device").symlink_to(device)
    for name, value in {"bNumInterfaces": str(interfaces), "idVendor": "0403",
                        "idProduct": "6001", "serial": "AC00U4RH",
                        "manufacturer": "FTDI", "product": "USB UART"}.items():
        (usb / name).write_text(value + "\n")
    (interface / "interface").write_text("UART A\n")
    (dev / port).touch()
    alias = dev / "navigation"
    alias.symlink_to(port)

    fs.create_file("/proc/tty/drivers", contents=f"usbserial /dev/{port[:-1]} 188 0-511 serial\n")
    assert [p.device for p in comports()] == [str(dev / port)]
    found = {p.device: p for p in comports(include_links=True)}
    assert set(found) == {str(dev / port), str(alias)}
    direct = found[str(dev / port)]
    linked = found[str(alias)]
    assert direct.location == ("1-3.3:1.0" if interfaces > 1 else "1-3.3")
    assert linked.device == str(alias)
    assert linked.name == "navigation"
    for attribute in ("location", "vid", "pid", "serial_number", "manufacturer",
                      "product", "interface", "description", "subsystem"):
        assert getattr(linked, attribute) == getattr(direct, attribute)
    assert linked.hwid == direct.hwid + " LINK=" + str(dev / port)


def test_link_without_sysfs_has_one_link_marker(fs):
    from serial.tools.list_ports_linux import SysFS

    dev = Path("/dev")
    fs.create_dir(dev)
    (dev / "ttyUSB1").touch()
    alias = dev / "navigation"
    alias.symlink_to("ttyUSB1")
    linked = SysFS(str(alias))
    assert linked.location is None
    assert linked.device == str(alias)
    assert linked.hwid.count("LINK=") == 1
