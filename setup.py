# setup.py for pyserial
#
# windows installer:
#  python setup.py bdist_wininst

import sys

from distutils.core import setup

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    if sys.version_info >= (3, 0):
        raise ImportError("build_py_2to3 not found in distutils - it is required for Python 3.x")
    from distutils.command.build_py import build_py
    suffix = ""
else:
    suffix = "-py3k"


if sys.version < '2.3':
    # distutils that old can't cope with the "classifiers" or "download_url"
    # keywords and True/False constants and basestring are missing
    raise ValueError("Sorry Python versions older than 2.3 are no longer"
                     "supported - check http://pyserial.sf.net for older "
                     "releases or upgrade your Python installation.")

setup(
    name = "pyserial" + suffix,
    description = "Python Serial Port Extension",
    version = "2.5",
    author = "Chris Liechti",
    author_email = "cliechti@gmx.net",
    url = "http://pyserial.sourceforge.net/",
    packages = ['serial'],
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
        'Topic :: Communications',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Terminals :: Serial',
    ],
    platforms = 'any',
    cmdclass = {'build_py': build_py},

    scripts = ['examples/miniterm.py'],
)
