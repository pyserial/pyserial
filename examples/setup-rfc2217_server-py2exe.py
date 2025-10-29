# setup script for py2exe to create the rfc2217_server.exe
#
# (C) 2001-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

import sys
from py2exe import freeze

sys.path.insert(0, '..')

freeze(
    zipfile=None,
    options={
        'dll_excludes': [],
        'includes': [
                'serial.urlhandler.protocol_hwgrep', 'serial.urlhandler.protocol_rfc2217',
                'serial.urlhandler.protocol_socket', 'serial.urlhandler.protocol_loop'],
        'dist_dir': 'bin',
        'excludes': ['serialjava', 'serialposix', 'serialcli'],
        'compressed': 1,
        'bundle_files': 1,
    },
    console=[
        "rfc2217_server.py",
    ],
)
