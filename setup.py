# setup.py for pySerial
#
# Direct install (all systems):
#   "python setup.py install"
#
# For Python 3.x use the corresponding Python executable,
# e.g. "python3 setup.py ..."
#
# (C) 2001-2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import serial
version = serial.VERSION

setup(
    name="pyserial",
    description="Python Serial Port Extension",
    version=version,
    author="Chris Liechti",
    author_email="cliechti@gmx.net",
    url="https://github.com/pyserial/pyserial",
    packages=['serial', 'serial.tools', 'serial.urlhandler', 'serial.threaded'],
    license="BSD",
    long_description="""\
Python Serial Port Extension for Win32, OSX, Linux, BSD, Jython, IronPython

Stable:

- Documentation: http://pythonhosted.org/pyserial/
- Download Page: https://pypi.python.org/pypi/pyserial

Latest:

- Documentation: http://pyserial.readthedocs.io/en/latest/
- Project Homepage: https://github.com/pyserial/pyserial
""",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Communications',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Terminals :: Serial',
    ],
    platforms='any',
    scripts=['serial/tools/miniterm.py'],
)
