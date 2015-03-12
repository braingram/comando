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

com = pycomando.handlers.ProtocolHandler(port)
text = pycomando.protocols.text.TextProtocol(com)
cmd = pycomando.protocols.command.CommandProtocol(com)

com.register_protocol(0, text)
com.register_protocol(1, cmd)


def show(bs):
    print("->%r" % bs)


def no_arg(cmd):
    print("->no_arg")


def bool_arg(cmd):
    print("->bool_arg %s, %s" % (cmd.get_arg(bool), cmd.get_arg(bool)))


def chr_arg(cmd):
    print("->chr_arg: args...")
    for i in xrange(5):
        c = cmd.get_arg(chr)
        print("\t%s: %s[%r]" % (i, ord(c), c))


def int_arg(cmd):
    print("->int_arg: args...")
    for i in xrange(5):
        print("\t%s: %s" % (i, cmd.get_arg(int)))


def float_arg(cmd):
    print("->float_arg: args...")
    for i in xrange(5):
        print("\t%s: %s" % (i, cmd.get_arg(float)))


text.receive_message = show
cmd.register_callback(0, no_arg)
cmd.register_callback(1, bool_arg)
cmd.register_callback(2, chr_arg)
cmd.register_callback(3, int_arg)
cmd.register_callback(4, float_arg)

print("\t<- from computer, -> = from arduino")

for msg in ('hi', 'how are you'):
    print("<-%r" % msg)
    text.send_message(msg)
    com.handle_stream()


for cid in (0, 1, 2, 3, 4):
    cmd.send_command(cid)
    com.handle_stream()
