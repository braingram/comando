#!/usr/bin/env python
"""
Send a receive a bunch of 'raw' messages
first byte [message length] 0-255 (does not include checksum)
last byte [checksum] 0-255, sum of bytes % 256
"""

import time

import serial


def build_message(bs):
    l = len(bs)
    if l > 255:
        raise Exception("Message is too long [%s > 255]" % l)
    cs = sum([ord(b) for b in bs]) % 256
    return chr(l) + bs + chr(cs)


def send(port, msg):
    print("Sending: %s" % repr(msg))
    port.write(msg)


def expect(port, msg):
    print port, repr(msg)
    n = port.read(1)
    print("\tRead n = %s" % repr(n))
    if n != '\x00':
        bs = port.read(ord(n))
    else:
        bs = ""
    print("\tRead bs = %s" % repr(bs))
    cs = port.read(1)
    print("\tRead cs = %s" % repr(cs))
    ccs = sum([ord(b) for b in bs]) % 256
    if ord(cs) != ccs:
        raise Exception("Invalid checksum %s != %s" % (ccs, ord(cs)))
    r = n + bs + cs
    if r != msg:
        raise Exception("Expected %s got %s" % (repr(msg), repr(r)))
    print("Received message: %s" % repr(r))
    return bs


port = serial.Serial('/dev/ttyACM0', 9600)
time.sleep(1)  # wait for arduino
port.setDTR(level=0)
time.sleep(1)

# this is the simplest message containing 0 bytes
#   first byte [message length] should be 0
#   the last byte [check sum] should also be 0
msg = '\x00\x00'
send(port, msg)
bs = expect(port, msg)

# this message contains some data but still a checksum of 0
msg = '\x01\x00\x00'
send(port, msg)
bs = expect(port, msg)

# these messages contains some data and a non-zero checksum
msg = '\x01\x01\x01'
send(port, msg)
bs = expect(port, msg)
msg = '\x01\xff\xff'
send(port, msg)
bs = expect(port, msg)

# this message contains >1 byte of data
msg = '\x02\x01\x02\x03'
send(port, msg)
bs = expect(port, msg)

# the checksum can roll over
msg = '\x02\xff\x01\x00'
send(port, msg)
bs = expect(port, msg)

# this message contains data (a byte string)
bs = '\x00\x01\x02\x03'
msg = build_message(bs)
assert len(msg) == len(bs) + 2
assert ord(msg[0]) == len(bs)
assert ord(msg[-1]) == sum([ord(b) for b in bs]) % 256
send(port, msg)
bs = expect(port, msg)
