# setup.py
from distutils.core import setup
from glob import glob

setup(
    name="pyserial",
    description="Python Serial Port Extension",
    version="1.1",
    author="Chris Liechti",
    author_email="cliechti@gmx.net",
    url="http://pyserial.sourceforge.net/",
    packages=['serial'],
)
