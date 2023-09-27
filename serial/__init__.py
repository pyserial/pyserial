#!/usr/bin/env python
#
# This is a wrapper module for different platform implementations
#
# This file is part of pySerial. https://github.com/pyserial/pyserial
# (C) 2001-2020 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

from __future__ import absolute_import

import sys
import importlib

from serial.serialutil import *
#~ SerialBase, SerialException, to_bytes, iterbytes

__version__ = '3.5'

VERSION = __version__

# pylint: disable=wrong-import-position
if sys.platform == 'cli':
    from serial.serialcli import Serial
else:
    import os
    # chose an implementation, depending on os
    if os.name == 'nt':  # sys.platform == 'win32':
        from serial.serialwin32 import Serial
    elif os.name == 'posix':
        from serial.serialposix import Serial, PosixPollSerial, VTIMESerial  # noqa
    elif os.name == 'java':
        from serial.serialjava import Serial
    else:
        raise ImportError("Sorry: no implementation for your platform ('{}') available".format(os.name))


protocol_handler_packages = [
    'serial.urlhandler',
]


def _find_module_for_protocol(protocol, packages):
    """Return the module that contains the handler for the specified protocol.
    
    If the protocol appears to be a fully qualified Python module (i.e. a.b.c), then use
    the package name (e.g. 'a.b' from the example 'a.b.c'), and use the final module name
    as the protocol name (e.g. 'c').
    """
    parts = protocol.split('.')
    if len(parts) > 1 and '' not in parts:
        # Treat the protocol as a full Python package name/path followed by the protocol name.
        protocol = parts[-1]
        packages = ['.'.join(parts[0:-1])]
    module_name = '.protocol_{}'.format(protocol)
    for package_name in packages:
        try:
            importlib.import_module(package_name)
            return importlib.import_module(module_name, package_name)
        except ImportError:
            continue
    return None


def serial_for_url(url, *args, **kwargs):
    """\
    Get an instance of the Serial class, depending on port/url. The port is not
    opened when the keyword parameter 'do_not_open' is true, by default it
    is. All other parameters are directly passed to the __init__ method when
    the port is instantiated.

    The list of package names that is searched for protocol handlers is kept in
    ``protocol_handler_packages``.

    e.g. we want to support a URL ``foobar://``. A module
    ``my_handlers.protocol_foobar`` is provided by the user. Then
    ``protocol_handler_packages.append("my_handlers")`` would extend the search
    path so that ``serial_for_url("foobar://"))`` would work.
    """
    # check and remove extra parameter to not confuse the Serial class
    do_open = not kwargs.pop('do_not_open', False)
    # the default is to use the native implementation
    klass = Serial
    try:
        url_lowercase = url.lower()
    except AttributeError:
        # it's not a string, use default
        pass
    else:
        # if it is an URL, try to import the handler module from the list of possible packages
        if '://' in url_lowercase:
            protocol = url_lowercase.split('://', 1)[0]
            handler_module = _find_module_for_protocol(protocol, protocol_handler_packages)
            if handler_module:
                if hasattr(handler_module, 'serial_class_for_url'):
                    url, klass = handler_module.serial_class_for_url(url)
                else:
                    klass = handler_module.Serial
            else:
                raise ValueError('invalid URL, protocol {!r} not known'.format(protocol))
    # instantiate and open when desired
    instance = klass(None, *args, **kwargs)
    instance.port = url
    if do_open:
        instance.open()
    return instance
