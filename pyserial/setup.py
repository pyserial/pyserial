# setup.py
from distutils.core import setup

#windows installer:
# python setup.py bdist_wininst

setup(
    name="pyserial",
    description="Python Serial Port Extension",
    version="2.0b2",
    author="Chris Liechti",
    author_email="cliechti@gmx.net",
    url="http://pyserial.sourceforge.net/",
    packages=['serial'],
    license="Python",
    long_description="Python Serial Port Extension for Win32, Linux, BSD, Jython",
    classifiers=[
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
