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

com = pycomando.handlers.StreamHandler(port)


def show(bs):
    print("Arduino said: " + bs)


com.receive_message = show

print("Computer saying: hi")
com.send_message("hi")

time.sleep(0.1)
while port.inWaiting():
    com.handle_stream()
