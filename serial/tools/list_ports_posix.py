import glob
import sys
import os
import re

try:
    import subprocess
except ImportError:
    def popen(argv):
        try:
            si, so =  os.popen4(' '.join(argv))
            return so.read().strip()
        except:
            raise IOError('lsusb failed')
else:
    def popen(argv):
        try:
            return subprocess.check_output(argv, stderr=subprocess.STDOUT).strip()
        except:
            raise IOError('lsusb failed')


# The comports function is expected to return an iterable that yields tuples of
# 3 strings: port name, human readable description and a hardware ID.
#
# as currently no method is known to get the second two strings easily, they
# are currently just identical to the port name.

# try to detect the OS so that a device can be selected...
plat = sys.platform.lower()

def read_line(filename):
    """help function to read a single line from a file. returns none"""
    try:
        f = open(filename)
        line = f.readline().strip()
        f.close()
        return line
    except IOError:
        return None

def re_group(regexp, text):
    """search for regexp in text, return 1st group on match"""
    m = re.search(regexp, text)
    if m: return m.group(1)


if   plat[:5] == 'linux':    # Linux (confirmed)
    # try to extract descriptions from sysfs. this was done by experimenting,
    # no guarantee that it works for all devices or in the future...

    def usb_sysfs_hw_string(sysfs_path):
        """given a path to a usb device in sysfs, return a string describing it"""
        bus, dev = os.path.basename(os.path.realpath(sysfs_path)).split('-')
        snr = read_line(sysfs_path+'/serial')
        if snr:
            snr_txt = ' SNR=%s' % (snr,)
        else:
            snr_txt = ''
        return 'USB VID:PID=%s:%s%s' % (
                read_line(sysfs_path+'/idVendor'),
                read_line(sysfs_path+'/idProduct'),
                snr_txt
                )

    def usb_lsusb_string(sysfs_path):
        bus, dev = os.path.basename(os.path.realpath(sysfs_path)).split('-')
        try:
            desc = popen(['lsusb', '-v', '-s', '%s:%s' % (bus, dev)])
            # descriptions from device
            iManufacturer = re_group('iManufacturer\s+\w+ (.+)', desc)
            iProduct = re_group('iProduct\s+\w+ (.+)', desc)
            iSerial = re_group('iSerial\s+\w+ (.+)', desc) or ''
            # descriptions from kernel
            idVendor = re_group('idVendor\s+0x\w+ (.+)', desc)
            idProduct = re_group('idProduct\s+0x\w+ (.+)', desc)
            # create descriptions. prefer text from device, fall back to the others
            return '%s %s %s' % (iManufacturer or idVendor, iProduct or idProduct, iSerial)
        except IOError:
            return base

    def describe(device):
        """\
        Get a human readable description.
        For USB-Serial devices try to run lsusb to get a human readable description.
        For USB-CDC devices read the description from sysfs.
        """
        base = os.path.basename(device)
        # USB-Serial devices
        sys_dev_path = '/sys/class/tty/%s/device/driver/%s' % (base, base)
        if os.path.exists(sys_dev_path):
            sys_usb = os.path.dirname(os.path.dirname(os.path.realpath(sys_dev_path)))
            return usb_lsusb_string(sys_usb)
        # USB-CDC devices
        sys_dev_path = '/sys/class/tty/%s/device/interface' % (base,)
        if os.path.exists(sys_dev_path):
            return read_line(sys_dev_path)
        return base

    def hwinfo(device):
        """Try to get a HW identification using sysfs"""
        base = os.path.basename(device)
        if os.path.exists('/sys/class/tty/%s/device' % (base,)):
            # PCI based devices
            sys_id_path = '/sys/class/tty/%s/device/id' % (base,)
            if os.path.exists(sys_id_path):
                return read_line(sys_id_path)
            # USB-Serial devices
            sys_dev_path = '/sys/class/tty/%s/device/driver/%s' % (base, base)
            if os.path.exists(sys_dev_path):
                sys_usb = os.path.dirname(os.path.dirname(os.path.realpath(sys_dev_path)))
                return usb_sysfs_hw_string(sys_usb)
            # USB-CDC devices
            if base.startswith('ttyACM'):
                sys_dev_path = '/sys/class/tty/%s/device' % (base,)
                if os.path.exists(sys_dev_path):
                    return usb_sysfs_hw_string(sys_dev_path + '/..')
        return 'n/a'    # XXX directly remove these from the list?

    def comports():
        devices = glob.glob('/dev/ttyS*') + glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
        return [(d, describe(d), hwinfo(d)) for d in devices]

elif plat == 'cygwin':       # cygwin/win32
    def comports():
        devices = glob.glob('/dev/com*')
        return [(d, d, d) for d in devices]

elif plat == 'openbsd3':    # BSD
    def comports():
        devices = glob.glob('/dev/ttyp*')
        return [(d, d, d) for d in devices]

elif plat[:3] == 'bsd' or  \
     plat[:7] == 'freebsd' or \
     plat[:7] == 'openbsd':  # BSD

    def comports():
        devices = glob.glob('/dev/cuad*')
        return [(d, d, d) for d in devices]

elif plat[:6] == 'darwin':   # OS X (confirmed)
    def comports():
        """scan for available ports. return a list of device names."""
        devices = glob.glob('/dev/tty.*')
        return [(d, d, d) for d in devices]

elif plat[:6] == 'netbsd':   # NetBSD
    def comports():
        """scan for available ports. return a list of device names."""
        devices = glob.glob('/dev/dty*')
        return [(d, d, d) for d in devices]

elif plat[:4] == 'irix':     # IRIX
    def comports():
        """scan for available ports. return a list of device names."""
        devices = glob.glob('/dev/ttyf*')
        return [(d, d, d) for d in devices]

elif plat[:2] == 'hp':       # HP-UX (not tested)
    def comports():
        """scan for available ports. return a list of device names."""
        devices = glob.glob('/dev/tty*p0')
        return [(d, d, d) for d in devices]

elif plat[:5] == 'sunos':    # Solaris/SunOS
    def comports():
        """scan for available ports. return a list of device names."""
        devices = glob.glob('/dev/tty*c')
        return [(d, d, d) for d in devices]

elif plat[:3] == 'aix':      # AIX
    def comports():
        """scan for available ports. return a list of device names."""
        devices = glob.glob('/dev/tty*')
        return [(d, d, d) for d in devices]

else:
    # platform detection has failed...
    sys.stderr.write("""\
don't know how to enumerate ttys on this system.
! I you know how the serial ports are named send this information to
! the author of this module:

sys.platform = %r
os.name = %r
pySerial version = %s

also add the naming scheme of the serial ports and with a bit luck you can get
this module running...
""" % (sys.platform, os.name, serial.VERSION))
    raise ImportError("Sorry: no implementation for your platform ('%s') available" % (os.name,))

# test
if __name__ == '__main__':
    for port, desc, hwid in sorted(comports()):
        print "%s: %s [%s]" % (port, desc, hwid)
