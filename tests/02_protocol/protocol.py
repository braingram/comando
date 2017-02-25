#!/usr/bin/env python
"""
A very simple comando example.
This does NOT use protocols and in that way is a BAD example
"""

import sys
import time

import serial

# play with the path so we can import pycomando even if it's nto installed
try:
    import pycomando
except ImportError:
    sys.path.append('../../')
    import pycomando

# connect to the serial port
port = serial.Serial('/dev/ttyACM0', 9600)
# if this is an arduino, reset it and wait
#time.sleep(1)  # wait for arduino
#port.setDTR(level=0)
#time.sleep(1)

# create our stream handler
com = pycomando.Comando(port)
# make a very simple text protocol
text = pycomando.protocols.TextProtocol(com)


# define a default message callback
# this will get called whenever a message is received
def show(bs):
    print("Arduino said: %s" % bs)


# tell the text protocol what to do when a message is received
text.receive_message = show

# register the text protocol with comando
com.register_protocol(0, text)

# send a message to the arduino
print("Computer saying: hi")
text.write("hi")

# wait a bit
time.sleep(0.1)
# handle the stream
while port.inWaiting():
    com.handle_stream()
