# setup script for py2exe to create the miniterm.exe
# $Id: setup-miniterm-py2exe.py,v 1.1 2005-09-21 19:51:19 cliechti Exp $

from distutils.core import setup
import glob, sys, py2exe, os

sys.path.append('..')

sys.argv.extend("py2exe --bundle 1".split())

import serial.tools.miniterm

setup(
    name = 'miniterm',
    zipfile = None,
    options = {"py2exe":
        {
            'dist_dir': 'bin',
            'excludes': ['serialjava', 'serialposix', 'serialcli'],
            'compressed': 1,
        }
    },
    console = [
        #~ "miniterm.py",
        serial.tools.miniterm.__file__
    ],
)
