#!/usr/bin/env python
from distutils.core import setup, Extension

import os
if os.name == 'nt':
    ext_modules =[
        Extension('_pyparallel',
            sources=['src/win32/_pyparallel.c'],
        )
    ]
else:
    ext_modules = None

setup (name = "pyparallel",
    description="Python Parallel Port Extension",
    version="0.1",
    author="Chris Liechti",
    author_email="cliechti@gmx.net",
    url="http://pyserial.sourceforge.net/",
    packages=['parallel'],
    license="Python",
    long_description="Python Parallel Port Extension for Win32, Linux, BSD",
    ext_modules = ext_modules
)
