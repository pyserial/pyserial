#!/usr/bin/env python
# setup.py
try:
    from setuptools import setup
except ImportError:
    print "standart distutils"
    from distutils.core import setup
else:
    print "setuptools"
import sys

#windows installer:
# python setup.py bdist_wininst

# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

import os
if os.name == 'nt':
    print "# set dependedcies for windows version"
    data_files = {'parallel': ['simpleio.dll']}
else:
    print "# no dependedcies"
    data_files = {}

setup(
    name = "pyparallel",
    description="Python Parallel Port Extension",
    version="0.2",
    author="Chris Liechti",
    author_email="cliechti@gmx.net",
    url="http://pyserial.sourceforge.net/",
    packages=['parallel'],
    license="Python",
    long_description="Python Parallel Port Extension for Win32, Linux, BSD",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Python Software Foundation License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Topic :: Communications',
        'Topic :: Software Development :: Libraries',
    ],
    package_data = data_files
)
