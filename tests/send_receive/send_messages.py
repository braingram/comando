#!/usr/bin/env python

import sys
import time

import serial

try:
    import pycomando
except ImportError:
    sys.path.append('../../')
    import pycomando

pycomando.protocols.command.test_type_conversion()

port = serial.Serial('/dev/ttyACM0', 9600)
time.sleep(1)  # wait for arduino
port.setDTR(level=0)
time.sleep(1)

com = pycomando.Comando(port)
text = pycomando.protocols.TextProtocol(com)
cmd = pycomando.protocols.CommandProtocol(com)

com.register_protocol(0, text)
com.register_protocol(1, cmd)


def show(bs):
    print("[echo]->%r" % bs)


def no_arg(cmd):
    print("[cmd]->no_arg")


def bool_arg(cmd):
    print("[cmd]->bool_arg: args...")
    for i in xrange(2):
        print("\t%s: %s" % (i, cmd.get_arg(bool)))


def chr_arg(cmd):
    print("[cmd]->chr_arg: args...")
    for i in xrange(5):
        c = cmd.get_arg(chr)
        print("\t%s: %s[%r]" % (i, ord(c), c))


def int_arg(cmd):
    print("[cmd]->int_arg: args...")
    for i in xrange(5):
        print("\t%s: %s" % (i, cmd.get_arg(int)))


def float_arg(cmd):
    print("[cmd]->float_arg: args...")
    for i in xrange(5):
        print("\t%s: %s" % (i, cmd.get_arg(float)))


def string_arg(cmd):
    print("[cmd]->string_arg: args...")
    for i in xrange(3):
        s = cmd.get_arg(str)
        print("\t%s: %s[%s]" % (i, s, len(s)))


text.receive_message = show
cmd.register_callback(0, no_arg)
cmd.register_callback(1, bool_arg)
cmd.register_callback(2, chr_arg)
cmd.register_callback(3, int_arg)
cmd.register_callback(4, float_arg)
cmd.register_callback(5, string_arg)

print("\t<- from computer, -> = from arduino")

for msg in ('hi', 'how are you'):
    print("[text]<-%r" % msg)
    text.send_message(msg)
    com.handle_stream()


cmds = [
    (0, ()),
    (1, (True, False)),
    (2, ('\r', '\n', 'a', 'Z', '\x00')),
    (3, (0, 1, -1, 1000000, -1000000)),
    (4, (0.0, 1.0, -1.0, 1.23, -123.0)),
    (5, ("hi", "hello", "")),
]

print
for (cid, args) in cmds:
    if len(args) == 0:
        args = None
    print
    print("[cmd]<- %s [%s]" % (cid, args))
    cmd.send_command(cid, args)
    time.sleep(0.5)
    while port.inWaiting():
        com.handle_stream()
time.sleep(0.5)
while port.inWaiting():
    com.handle_stream()
