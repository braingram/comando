#!/usr/bin/env python

import sys
import time

import serial

try:
    import pycomando
except ImportError:
    sys.path.append('../../')
    import pycomando

port = serial.Serial('/dev/ttyACM0', 9600)
time.sleep(1)  # wait for arduino
port.setDTR(level=0)
time.sleep(1)

h = pycomando.handlers.StreamHandler(port)

print("\t<- from computer, -> = from arduino")


def show(bs):
    print("->%r" % bs)

h.on_message = show

msg = "\x00hi"
print("<-%r" % msg)
h.write(msg)
h.read()

msg = "\x00how are you"
print("<-%r" % msg)
h.write(msg)
h.read()
