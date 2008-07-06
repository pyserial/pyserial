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

setup(
    name="pyserial",
    description="Python Serial Port Extension",
    version="2.4",
    author="Chris Liechti",
    author_email="cliechti@gmx.net",
    url="http://pyserial.sourceforge.net/",
    packages=['serial'],
    license="Python",
    long_description="Python Serial Port Extension for Win32, Linux, BSD, Jython",
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Python Software Foundation License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Topic :: Communications',
        'Topic :: Software Development :: Libraries',
        'Topic :: Terminals :: Serial',
    ],
)
