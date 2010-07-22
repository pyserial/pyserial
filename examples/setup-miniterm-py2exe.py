# setup script for py2exe to create the miniterm.exe
# $Id: setup-miniterm-py2exe.py,v 1.1 2005-09-21 19:51:19 cliechti Exp $

from distutils.core import setup
import glob, sys, py2exe, os

sys.path.append('..')

sys.argv.extend("py2exe --bundle 1".split())

setup(
    name='miniterm',
    #~ version='0.5',
    zipfile=None,
    options = {"py2exe":
        {
            'dist_dir': 'bin',
            'excludes': ['javax.comm'],
            'compressed': 1,
        }
    },
    console = [
        #~ "miniterm_exe_wrapper.py",
        "miniterm.py",
    ],
)
