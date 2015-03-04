#!/usr/bin/env python

import struct

import serial


port = '/dev/ttyUSB0'
baud = 9600

# create stream
s = serial.Serial(port, baud)

# create stream handler
# this reads/writes to the stream
# and simply passes messages on to other protocols
h = StreamHandler(s)

# register a few protocols
h.register_protocol(0, VerboseProtocol())
h.register_protocol(1, PackedProtocol())


def pong():
    print("Pong!")


def receive(arg):
    print("Received: %s" % arg)

# register a few commands
h.register_command('ping')
h.register_command('pong', callback=pong)
h.register_command('transmit', nargs=1)
h.register_command('receive', callback=receive)

# register some basic types
h.register_type(0, int)
h.register_type(1, float)
h.register_type(2, str)


# get the command namespace
ns = h.namespace

# ping it
ns.ping()
h.handle()  # this could be called asynchronously

# can send multiple types with the same command
ns.transmit(0)
h.handle()

ns.transmit(0.1)
h.handle()

ns.transmit("hi")
h.handle()
