#!/usr/bin/env python
"""
Call a couple commands
0 [na]: toggle blink
1 [bool]: set blink to on/off
2 [int]: set blink delay
3 [float]: echo a float
"""

import struct
import time

import serial


def build_message(bs):
    l = len(bs)
    if l > 255:
        raise Exception("Message is too long [%s > 255]" % l)
    cs = sum([ord(b) for b in bs]) % 256
    return chr(l) + bs + chr(cs)


def read_in_all(port, wait=False):
    if wait:
        while port.inWaiting() == 0:
            time.sleep(0.01)
    msg = ""
    while port.inWaiting():
        msg += port.read(1)
        if wait:
            time.sleep(0.01)
    return msg


def send(port, msg):
    print("Sending: %s" % repr(msg))
    port.write(msg)
    print(repr(read_in_all(port)))


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


print("Echo a few floats")
for f in (0, 0.001, 0.0001, 12345.0, 0.0347734):
    send(port, build_message('\x03' + struct.pack('f', f)))
    s = repr(read_in_all(port, wait=True))
    print(f, s)

send(port, build_message('\x02' + struct.pack('I', 500)))
print(repr(read_in_all(port, wait=True)))

print("Start blinking")
send(port, build_message('\x01\x01'))
time.sleep(3)

# toggle blinking
print("Toggle blinking")
send(port, build_message('\x00'))
time.sleep(3)
print("Toggle blinking")
send(port, build_message('\x00'))

print("Increase blinking")
send(port, build_message('\x02' + struct.pack('I', 100)))
time.sleep(3)

print("Decrease blinking")
send(port, build_message('\x02' + struct.pack('I', 1000)))
time.sleep(3)

print("Stop blinking")
send(port, build_message('\x01\x00'))
