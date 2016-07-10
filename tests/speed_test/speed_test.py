#!/usr/bin/env python
"""
Time sending/receiving bytes
"""

import time

import serial

import pycomando

conn = serial.Serial('/dev/ttyACM0', 115200)
com = pycomando.Comando(conn)
text = pycomando.protocols.TextProtocol(com)
cmd = pycomando.protocols.CommandProtocol(com)

com.register_protocol(0, text)
com.register_protocol(1, cmd)

global result
result = None


def show(text):
    print text


def receive_ping(cmd):
    global result
    result = [
        cmd.get_arg(float),
        cmd.get_arg(float),
        cmd.get_arg(float)]


def send_ping(v):
    global result
    result = None
    vs = (float(v), float(v+1), float(v+2))
    t0 = time.time()
    # send value
    cmd.send_command(0, vs)
    # handle stream
    while result is None:
        com.handle_stream()
    # get value
    t1 = time.time()
    for (v, r) in zip(vs, result):
        assert (r - v) < 0.0001, "%s, %s" % (r, v)
    return t1 - t0

text.register_callback(show)

cmd.register_callback(0, receive_ping)


ts = []
for i in xrange(1000):
    ts.append(send_ping(i))

print "times:", ts
print "\tmean: %s" % (sum(ts) / len(ts), )
print "\tmax : %s" % (max(ts), )
