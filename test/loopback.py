"""
This script sends back any data, creating a loopback connection.

It uses "socat -d -d pty,raw,echo=0 pty,raw,echo=0" to create a connected
tunnel and then mirrors back all the data received on one end.

can be used to run some of the tests with a virtual serial port.
"""

import subprocess
import shlex
import serial
import re

socat = subprocess.Popen(
    shlex.split('socat -d -d pty,raw,echo=0 pty,raw,echo=0'),
    stderr=subprocess.PIPE,
    encoding='utf-8')
first_port = re.search(r'PTY is (/dev/pts/\d+)', socat.stderr.readline()).group(1)
second_port = re.search(r'PTY is (/dev/pts/\d+)', socat.stderr.readline()).group(1)
print(f'connect test to {first_port}')
try:
    with serial.serial_for_url(second_port, inter_byte_timeout=0.1) as ser:
        while True:
            ser.write(ser.read())
except KeyboardInterrupt:
    print()
finally:
    socat.kill()
