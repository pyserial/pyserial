#!/usr/bin/env python

# portable serial port access with python
# this is a wrapper module for different platform implementations of the
# port enumeration feature
#
# (C) 2011 Chris Liechti <cliechti@gmx.net>
# this is distributed under a free software license, see license.txt

"""\
This module will provide a function called comports that returns an
iterable (generator or list) that will enumerate available com ports. Note that
on some systems non-existent ports may be listed.

Additionally a grep function is supplied that can be used to search for ports
based on their descriptions or hardware ID.
"""

import sys, os, re

# chose an implementation, depending on os
#~ if sys.platform == 'cli':
#~ else:
import os
# chose an implementation, depending on os
if os.name == 'nt': #sys.platform == 'win32':
    from list_ports_windows import *
elif os.name == 'posix':
    from list_ports_posix import *
#~ elif os.name == 'java':
else:
    raise ImportError("Sorry: no implementation for your platform ('%s') available" % (os.name,))


def grep(regexp):
    """\
    Search for ports using a regular expression. Port name, description and
    hardware ID are searched. The function returns an iterable that returns the
    same tuples as comport() would do.
    """
    for port, desc, hwid in comports():
        if re.search(regexp, port) or re.search(regexp, desc) or re.search(regexp, hwid):
            yield port, desc, hwid

# test
if __name__ == '__main__':
    hits = 0
    if len(sys.argv) > 1:
        print "Filtered list with regexp: %r" % (sys.argv[1],)
        for port, desc, hwid in sorted(grep(sys.argv[1])):
            print "%-20s: %s [%s]" % (port, desc, hwid)
            hits += 1
    else:
        for port, desc, hwid in sorted(comports()):
            print "%-20s: %s [%s]" % (port, desc, hwid)
            hits += 1
    if hits:
        print "%d ports found" % (hits,)
    else:
        print "no ports found"
