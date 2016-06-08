#!/usr/bin/env python
#
# This is a module that gathers a list of serial ports including details on OSX
#
# code originally from https://github.com/makerbot/pyserial/tree/master/serial/tools
# with contributions from cibomahto, dgs3, FarMcKon, tedbrandston
# and modifications by cliechti, hoihu, hardkrash
#
# This file is part of pySerial. https://github.com/pyserial/pyserial
# (C) 2013-2015
#
# SPDX-License-Identifier:    BSD-3-Clause


# List all of the callout devices in OS/X by querying IOKit.

# See the following for a reference of how to do this:
# http://developer.apple.com/library/mac/#documentation/DeviceDrivers/Conceptual/WorkingWSerial/WWSerial_SerialDevs/SerialDevices.html#//apple_ref/doc/uid/TP30000384-CIHGEAFD

# More help from darwin_hid.py

# Also see the 'IORegistryExplorer' for an idea of what we are actually searching

import ctypes
import ctypes.util

from serial.tools import list_ports_common

iokit = ctypes.cdll.LoadLibrary(ctypes.util.find_library('IOKit'))
cf = ctypes.cdll.LoadLibrary(ctypes.util.find_library('CoreFoundation'))

kIOMasterPortDefault = ctypes.c_void_p.in_dll(iokit, "kIOMasterPortDefault")
kCFAllocatorDefault = ctypes.c_void_p.in_dll(cf, "kCFAllocatorDefault")

kCFStringEncodingMacRoman = 0

iokit.IOServiceMatching.restype = ctypes.c_void_p

iokit.IOServiceGetMatchingServices.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
iokit.IOServiceGetMatchingServices.restype = ctypes.c_void_p

iokit.IORegistryEntryGetParentEntry.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]

iokit.IORegistryEntryCreateCFProperty.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32]
iokit.IORegistryEntryCreateCFProperty.restype = ctypes.c_void_p

iokit.IORegistryEntryGetPath.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
iokit.IORegistryEntryGetPath.restype = ctypes.c_void_p

iokit.IORegistryEntryGetName.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
iokit.IORegistryEntryGetName.restype = ctypes.c_void_p

iokit.IOObjectGetClass.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
iokit.IOObjectGetClass.restype = ctypes.c_void_p

iokit.IOObjectRelease.argtypes = [ctypes.c_void_p]


cf.CFStringCreateWithCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int32]
cf.CFStringCreateWithCString.restype = ctypes.c_void_p

cf.CFStringGetCStringPtr.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
cf.CFStringGetCStringPtr.restype = ctypes.c_char_p

cf.CFNumberGetValue.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p]
cf.CFNumberGetValue.restype = ctypes.c_void_p

# void CFRelease ( CFTypeRef cf );
cf.CFRelease.argtypes = [ctypes.c_void_p]
cf.CFRelease.restype = None

# CFNumber type defines
kCFNumberSInt8Type = 1
kCFNumberSInt16Type = 2
kCFNumberSInt32Type = 3
kCFNumberSInt64Type = 4


def get_string_property(device_type, property):
    """
    Search the given device for the specified string property

    @param device_type Type of Device
    @param property String to search for
    @return Python string containing the value, or None if not found.
    """
    key = cf.CFStringCreateWithCString(
            kCFAllocatorDefault,
            property.encode("mac_roman"),
            kCFStringEncodingMacRoman)

    CFContainer = iokit.IORegistryEntryCreateCFProperty(
            device_type,
            key,
            kCFAllocatorDefault,
            0)
    output = None

    if CFContainer:
        output = cf.CFStringGetCStringPtr(CFContainer, 0)
        if output is not None:
            output = output.decode('mac_roman')
        cf.CFRelease(CFContainer)
    return output


def get_int_property(device_type, property, cf_number_type):
    """
    Search the given device for the specified string property

    @param device_type Device to search
    @param property String to search for
    @param cf_number_type CFType number

    @return Python string containing the value, or None if not found.
    """
    key = cf.CFStringCreateWithCString(
            kCFAllocatorDefault,
            property.encode("mac_roman"),
            kCFStringEncodingMacRoman)

    CFContainer = iokit.IORegistryEntryCreateCFProperty(
            device_type,
            key,
            kCFAllocatorDefault,
            0)

    if CFContainer:
        if (cf_number_type == kCFNumberSInt32Type):
            number = ctypes.c_uint32()
        elif (cf_number_type == kCFNumberSInt16Type):
            number = ctypes.c_uint16()
        cf.CFNumberGetValue(CFContainer, cf_number_type, ctypes.byref(number))
        cf.CFRelease(CFContainer)
        return number.value
    return None


def IORegistryEntryGetName(device):
    pathname = ctypes.create_string_buffer(100)  # TODO: Is this ok?
    iokit.IOObjectGetClass(device, ctypes.byref(pathname))
    return pathname.value


def GetParentDeviceByType(device, parent_type):
    """ Find the first parent of a device that implements the parent_type
        @param IOService Service to inspect
        @return Pointer to the parent type, or None if it was not found.
    """
    # First, try to walk up the IOService tree to find a parent of this device that is a IOUSBDevice.
    parent_type = parent_type.encode('mac_roman')
    while IORegistryEntryGetName(device) != parent_type:
        parent = ctypes.c_void_p()
        response = iokit.IORegistryEntryGetParentEntry(
                device,
                "IOService".encode("mac_roman"),
                ctypes.byref(parent))
        # If we weren't able to find a parent for the device, we're done.
        if response != 0:
            return None
        device = parent
    return device


def GetIOServicesByType(service_type):
    """
    returns iterator over specified service_type
    """
    serial_port_iterator = ctypes.c_void_p()

    iokit.IOServiceGetMatchingServices(
            kIOMasterPortDefault,
            iokit.IOServiceMatching(service_type.encode('mac_roman')),
            ctypes.byref(serial_port_iterator))

    services = []
    while iokit.IOIteratorIsValid(serial_port_iterator):
        service = iokit.IOIteratorNext(serial_port_iterator)
        if not service:
            break
        services.append(service)
    iokit.IOObjectRelease(serial_port_iterator)
    return services


def location_to_string(locationID):
    """
    helper to calculate port and bus number from locationID
    """
    loc = ['{}-'.format(locationID >> 24)]
    while locationID & 0xf00000:
        if len(loc) > 1:
            loc.append('.')
        loc.append('{}'.format((locationID >> 20) & 0xf))
        locationID <<= 4
    return ''.join(loc)


class SuitableSerialInterface(object):
    pass


def scan_interfaces():
    """
    helper function to scan USB interfaces
    returns a list of SuitableSerialInterface objects with name and id attributes
    """
    interfaces = []
    for service in GetIOServicesByType('IOSerialBSDClient'):
        device = get_string_property(service, "IOCalloutDevice")
        if device:
            usb_device = GetParentDeviceByType(service, "IOUSBInterface")
            if usb_device:
                name = get_string_property(usb_device, "USB Interface Name") or None
                locationID = get_int_property(usb_device, "locationID", kCFNumberSInt32Type) or ''
                i = SuitableSerialInterface()
                i.id = locationID
                i.name = name
                interfaces.append(i)
    return interfaces


def search_for_locationID_in_interfaces(serial_interfaces, locationID):
    for interface in serial_interfaces:
        if (interface.id == locationID):
            return interface.name
    return None


def comports():
    # Scan for all iokit serial ports
    services = GetIOServicesByType('IOSerialBSDClient')
    ports = []
    serial_interfaces = scan_interfaces()
    for service in services:
        # First, add the callout device file.
        device = get_string_property(service, "IOCalloutDevice")
        if device:
            info = list_ports_common.ListPortInfo(device)
            # If the serial port is implemented by IOUSBDevice
            usb_device = GetParentDeviceByType(service, "IOUSBDevice")
            if usb_device:
                # fetch some useful informations from properties
                info.vid = get_int_property(usb_device, "idVendor", kCFNumberSInt16Type)
                info.pid = get_int_property(usb_device, "idProduct", kCFNumberSInt16Type)
                info.serial_number = get_string_property(usb_device, "USB Serial Number")
                info.product = get_string_property(usb_device, "USB Product Name") or 'n/a'
                info.manufacturer = get_string_property(usb_device, "USB Vendor Name")
                locationID = get_int_property(usb_device, "locationID", kCFNumberSInt32Type)
                info.location = location_to_string(locationID)
                info.interface = search_for_locationID_in_interfaces(serial_interfaces, locationID)
                info.apply_usb_info()
            ports.append(info)
    return ports

# test
if __name__ == '__main__':
    for port, desc, hwid in sorted(comports()):
        print("{}: {} [{}]".format(port, desc, hwid))
