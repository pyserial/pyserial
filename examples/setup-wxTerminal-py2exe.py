# This is a setup.py example script for the use with py2exe
#
# (C) 2001-2015 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

import os
import sys
from py2exe import freeze

sys.path.insert(0, '..')

# this script is only useful for py2exe so just run that distutils command.
# that allows to run it with a simple double click.

# get an icon from somewhere.. the python installation should have one:
# icon = os.path.join(os.path.dirname(sys.executable), 'py.ico')

freeze(
    options={
        'excludes': ['javax.comm'],
        'optimize': 2,
        'dist_dir': 'dist',
    },

    windows=[
        {
            'script': "wxTerminal.py",
            # 'icon_resources': [(0x0004, icon)]
        },
    ],
    zipfile="stuff.lib",

    version_info=dict(
        product_name="wxTerminal",
        description="Simple serial terminal application",
        version="0.1",
        copyright="Chris Liechti <cliechti@gmx.net>",
        comments="https://github.com/pyserial/pyserial/",
    ),
)
