#!/usr/bin/env python

import serial
import time

port = serial.Serial('/dev/ttyACM0', 9600)
time.sleep(1)
port.write('\x00\x00')
print(repr(port.read(2)))
