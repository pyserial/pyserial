# setup.py for pySerial
#
# Windows installer:
#   "python setup.py bdist_wininst"
#
# Direct install (all systems):
#   "python setup.py install"
#
# For Python 3.x use the corresponding Python executable,
# e.g. "python3 setup.py ..."

import sys

from distutils.core import setup

if sys.version_info >= (3, 0):
    try:
        from distutils.command.build_py import build_py_2to3 as build_py
        from distutils.command.build_scripts import build_scripts_2to3 as build_scripts
    except ImportError:
        raise ImportError("build_py_2to3 not found in distutils - it is required for Python 3.x")
    else:
        sys.stderr.write('Detected Python 3, using 2to3\n')
else:
    from distutils.command.build_py import build_py
    from distutils.command.build_scripts import build_scripts


if sys.version < '2.3':
    # distutils that old can't cope with the "classifiers" or "download_url"
    # keywords and True/False constants and basestring are missing
    raise ValueError("Sorry Python versions older than 2.3 are no longer"
                     "supported - check http://pyserial.sf.net for older "
                     "releases or upgrade your Python installation.")

# importing version does not work with Python 3 as files have not yet been
# converted.
#~ import serial
#~ version = serial.VERSION

import re, os
version = re.search(
        "VERSION.*'(.+)'",
        open(os.path.join('serial', '__init__.py')).read()).group(1)


setup(
    name = "pyserial",
    description = "Python Serial Port Extension",
    version = version,
    author = "Chris Liechti",
    author_email = "cliechti@gmx.net",
    url = "http://pyserial.sourceforge.net/",
    packages = ['serial', 'serial.tools', 'serial.urlhandler'],
    license = "Python",
    long_description = "Python Serial Port Extension for Win32, Linux, BSD, Jython, IronPython",
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Python Software Foundation License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        #~ 'Operating System :: Microsoft :: Windows :: Windows CE', # could work due to new ctypes impl. someone needs to confirm that
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.3',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Communications',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Terminals :: Serial',
    ],
    platforms = 'any',
    cmdclass = {'build_py': build_py, 'build_scripts': build_scripts},
    use_2to3 = sys.version_info >= (3, 0), # for distribute

    scripts = ['serial/tools/miniterm.py'],
)
