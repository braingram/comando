#!/usr/bin/env python

import ctypes
import sys
import time

import serial

try:
    import pycomando
except ImportError:
    sys.path.append('../../')
    import pycomando

if sys.version_info >= (3, 0):
    xrange = range

pycomando.protocols.command.test_type_conversion()

port = serial.Serial('/dev/ttyACM0', 9600)
# time.sleep(1)  # wait for arduino
# port.setDTR(level=0)
# time.sleep(1)

com = pycomando.Comando(port)
text = pycomando.protocols.TextProtocol(com)
cmd = pycomando.protocols.CommandProtocol(com)

com.register_protocol(0, text)
com.register_protocol(1, cmd)

cmds = [
    (0, None, ()),
    # (1, ctypes.c_bool, (True, False)),
    (1, bool, (True, False)),
    (2, ctypes.c_char, (b'\r', b'\n', b'a', b'Z', b'\x00')),
    # (3, ctypes.c_int32, (0, 1, -1, 1000000, -1000000)),
    (3, int, (0, 1, -1, 1000000, -1000000)),
    # (4, ctypes.c_float, (0.0, 1.0, -1.0, 1.23, -123.0)),
    (4, float, (0.0, 1.0, -1.0, 1.23, -123.0)),
    (5, str, ("hi", "hello", "")),
]


def show(bs):
    print("[echo]->%r" % bs)


def get_value(v):
    if hasattr(v, 'value'):
        return v.value
    return v


def no_arg(cmd):
    print("[cmd]->no_arg")
    assert cmd.has_arg() == False


def bool_arg(cmd):
    print("[cmd]->bool_arg: args...")
    for i in xrange(2):
        assert cmd.has_arg()
        a = get_value(cmd.get_arg(cmds[1][1]))
        print("\t%s: %s" % (i, a))
        assert a == cmds[1][2][i], "%s, %s" % (a, cmds[1][2][i])


def chr_arg(cmd):
    print("[cmd]->chr_arg: args...")
    for i in xrange(5):
        assert cmd.has_arg()
        c = get_value(cmd.get_arg(cmds[2][1]))
        print("\t%s: %s[%r]" % (i, ord(c), c))
        assert c == cmds[2][2][i], "%s, %s" % (c, cmds[2][2][i])


def int_arg(cmd):
    print("[cmd]->int_arg: args...")
    for i in xrange(5):
        assert cmd.has_arg()
        a = get_value(cmd.get_arg(cmds[3][1]))
        print("\t%s: %s" % (i, a))
        assert a == cmds[3][2][i], "%s, %s" % (a, cmds[3][2][i])


def float_arg(cmd):
    print("[cmd]->float_arg: args...")
    for i in xrange(5):
        assert cmd.has_arg()
        a = get_value(cmd.get_arg(cmds[4][1]))
        print("\t%s: %s" % (i, a))
        assert abs(a - cmds[4][2][i]) < 0.001, "%s, %s" % (a, cmds[4][2][i])


def string_arg(cmd):
    print("[cmd]->string_arg: args...")
    for i in xrange(3):
        assert cmd.has_arg()
        s = cmd.get_arg(cmds[5][1])
        print("\t%s: %s[%s]" % (i, s, len(s)))
        assert s == cmds[5][2][i], "%s, %s" % (s, cmds[5][2][i])


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


print()
for (cid, t, args) in cmds:
    if len(args) == 0:
        args = None
    else:
        args = [t(a) for a in args]
    print()
    print("[cmd]<- %s [%s]" % (cid, args))
    cmd.send_command(cid, args)
    time.sleep(0.5)
    while port.inWaiting():
        com.handle_stream()
time.sleep(0.5)
while port.inWaiting():
    com.handle_stream()
