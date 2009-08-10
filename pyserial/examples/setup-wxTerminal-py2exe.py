# This is a setup.py example script for the use with py2exe
from distutils.core import setup
import py2exe
import sys, os

#this script is only useful for py2exe so just run that distutils command.
#that allows to run it with a simple double click.
sys.argv.append('py2exe')

#get an icon from somewhere.. the python installation should have one:
icon = os.path.join(os.path.dirname(sys.executable), 'py.ico')

setup(
    options = {'py2exe': {
        'excludes': ['javax.comm'],
        'optimize': 2,
        'dist_dir': 'dist',
        }
    },

    name = "wxTerminal",
    windows = [
        {
            'script': "wxTerminal.py",
            'icon_resources': [(0x0004, icon)]
        },
    ],
    zipfile = "stuff.lib",

    description = "Simple serial terminal application",
    version = "0.1",
    author = "Chris Liechti",
    author_email = "cliechti@gmx.net",
    url = "http://pyserial.sf.net",
)
