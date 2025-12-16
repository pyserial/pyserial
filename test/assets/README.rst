pyserial test assets
####################

The files in this directory are test assets.
The test suite uses them to recreate the state of a device on a system
to help ensure that pyserial is able to reliably identify devices.

In general, each test asset should have a descriptive filename,
perhaps following a template like:

..  code-block::

    {MANUFACTURER}--{PRODUCT_NAME}.json

In addition, the ``"context"`` section of the JSON file needs to be filled out.
The context has no schema, but all relevant information about the device
should be included so that it's clear to future readers and developers
what the device was, or what commands were run to create the pseudoterminal,
etc.

A test can them be added. You should use your best judgement,
but the test should verify the information that pyserial *should* return
for the individual port, as well as when all ports are listed.

This code snippet is a starting point for a new test:

..  code-block:: python

    def test_{manufacturer}_{product}(prepare_filesystem):
        #     ^^^^^^^^^^^^   ^^^^^^^  Change these!
        """Test sysfs loading for the {manufacturer} {product}."""
        #                              ^^^^^^^^^^^^   ^^^^^^^ Change these!

        prepare_filesystem("assets/sysfs/CHANGEME.json")

        info = serial.tools.list_ports_linux.SysFS("/dev/CHANGEME")

        assert info.device == "CHANGEME"
        assert info.name == "CHANGEME"
        assert info.description == "CHANGEME"
        assert info.hwid == "CHANGEME"
        assert info.vid == 0x0000
        assert info.pid == 0x0000
        assert info.serial_number is None or "CHANGEME"
        assert info.location == "CHANGEME"
        assert info.manufacturer == "CHANGEME"
        assert info.product == "CHANGEME"
        assert info.interface is None or "CHANGEME"
        assert info.usb_device_path == "CHANGEME"
        assert info.device_path == "CHANGEME"
        assert info.subsystem == "CHANGEME"
        assert info.usb_interface_path == "CHANGEME"

        ports = serial.tools.list_ports_linux.comports()
        assert len(ports) == 1
        assert ports[0].device == "/dev/CHANGEME"
