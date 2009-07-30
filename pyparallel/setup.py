#!/usr/bin/env python
from distutils.core import setup

import os
if os.name == 'nt':
    data_files = {'parallel': ['simpleio.dll']}
else:
    data_files = None

setup (name = "pyparallel",
    description="Python Parallel Port Extension",
    version="0.2",
    author="Chris Liechti",
    author_email="cliechti@gmx.net",
    url="http://pyserial.sourceforge.net/",
    packages=['parallel'],
    license="Python",
    long_description="Python Parallel Port Extension for Win32, Linux, BSD",
    package_data = data_files
)
