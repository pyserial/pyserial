#!/usr/bin/env python 
#portable parallel port access with python
#this is a wrapper module for different platform implementations
#
# (C)2001-2002 Chris Liechti <cliechti@gmx.net>
# this is distributed under a free software license, see license.txt

import sys, os, string
VERSION = string.split("$Revision: 1.4 $")[1]     #extract CVS version

#chose an implementation, depending on os
if os.name == 'nt':
    from parallelwin32 import *
elif os.name == 'posix':
    if sys.platform == 'linux2':
        from parallelppdev import *     #linux, kernel 2.4
    else:
        from parallelioctl import *     #IOCTLs
elif os.name == 'java':
    from paralleljava import *
else:
    raise "Sorry no implementation for your platform available."
