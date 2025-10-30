from android.hardware.usb import UsbManager
from serial.android import get_android_context
from serial.tools import list_ports_common


def comports():
    context = get_android_context()
    usb_manager: UsbManager = context.getSystemService(context.USB_SERVICE)
    device_list = usb_manager.getDeviceList()
    device_keys = list(device_list.keySet().toArray())
    devices = []
    for usb_device_key in device_keys:
        usb_device = device_list.get(usb_device_key)
        info = list_ports_common.ListPortInfo(usb_device_key, True)
        info.vid = usb_device.getVendorId()
        info.pid = usb_device.getProductId()
        # needs permission
        # info.serial_number = usb_device.getSerialNumber()
        info.manufacturer = usb_device.getManufacturerName()
        info.product = usb_device.getProductName()
        info.interface = usb_device.getInterface(0)
        info.hwid = usb_device.getDeviceId()
        info.name = usb_device.getDeviceName()
        devices.append(info)
    return devices
