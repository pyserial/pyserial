#! python
#
# Enumerate serial ports on Windows including a human readable description
# and hardware information using winreg.
#
# Using winreg helps find virtual comports

try:
    # Python 3.X
    import winreg
except ImportError:
    # Python 2.7 compatibility
    try:
        import _winreg as winreg
    except ImportError:
        winreg = None

from serial.tools import list_ports_common
from serial.tools import list_ports_windows


SERIAL_REGISTRY_PATH = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'


def regval_to_ListPortInfo(winport):
    """Convert a windows port from registry key to pyserial's ListPortInfo.

    Args:
        winport (tuple): Windows registry value (description, device, value).
    """
    # Create the ListPortInfo
    description, device, _ = winport
    listport = list_ports_common.ListPortInfo(device)

    # Format the description like other ListPortInfo
    description = description.replace('\\Device\\', '')
    listport.description = "{} ({})".format(description, device)

    return listport
# end regval_to_ListPortInfo


def winreg_comports():
    """Return windows comports found in the registry.

    See Also:
        list_ports_winreg.comports(), list_ports_winreg.comports_list(),
        list_ports_windows.comports()

    Note:
        This should include virtual comports, and it is significantly faster
        than list_ports_windows.comports(). However, list_ports_windows has far
        more information. comports() contains all list_ports_windows.comports()
        and winreg_comports() that were not found from list_ports_windows.

    Returns:
        comports (list): Sorted list of ListPortInfo.
    """
    try:
        # Get the Serial Coms registry
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, SERIAL_REGISTRY_PATH)

        # Get key info - number of values (subkeys, num_vals, last_modified)
        num_values = winreg.QueryInfoKey(key)[1]

        # Make a generator of comports
        for i in range(num_values):        
            # get registry value for the comport
            value = winreg.EnumValue(key, i)
            yield regval_to_ListPortInfo(value)

        # Close the registry key
        winreg.CloseKey(key)
    except (AttributeError, WindowsError, EnvironmentError):
        # winreg is None or there was a key error
        pass
# end winreg_comports


def comports_list():
    """Return a list of comports found from list_ports_windows and comports
    found in the window registry.
    
    See Also:
        list_ports_winreg.comports(), list_ports_winreg.winreg_comports(),
        list_ports_windows.comports()

    Note:
        This should include virtual comports. This method contains all
        list_ports_windows.comports() and winreg_comports() that were not found
        from list_ports_windows.

    Returns:
        comports (list): List of ListPortInfo comport details.
    """
    comports = list(list_ports_windows.comports())

    comports[len(comports): ] = [li for li in winreg_comports()
                                 if li not in comports]

    return comports
# end comports_list


def comports():
    """Generator for comports found from list ports windows and comports found
    in the windows registry.

    See Also:
        list_ports_winreg.comports_list(), list_ports_winreg.winreg_comports(),
        list_ports_windows.comports()

    Note:
        This should include virtual comports. This method contains all
        list_ports_windows.comports() and winreg_comports() that were not found
        from list_ports_windows.

    Yields:
        comport (ListPortInfo): Comport details.

    Returns:
        comports (generator): Generator of ListPortInfo comports.
    """
    existing = []
    for comport in list_ports_windows.comports():
        existing.append(comport)
        yield comport

    for li in winreg_comports():
        if li not in existing:
            existing.append(li)
            yield li
# end comports


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# test
if __name__ == '__main__':
    for port, desc, hwid in sorted(comports()):
        print("%s: %s [%s]" % (port, desc, hwid))
