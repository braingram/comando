#!/usr/bin/env python
"""
Time sending/receiving bytes
"""

import time

import serial

conn = serial.Serial('/dev/ttyACM0', 115200)
if conn.inWaiting():
    conn.readline()


def send_ping(v):
    vs = (float(v), float(v+1), float(v+2))
    t0 = time.time()
    # send value
    conn.write("%0.4f,%0.4f,%0.4f\n" % (vs))
    results = map(float, conn.readline().strip().split(','))
    t1 = time.time()
    for (v, r) in zip(vs, results):
        assert (r - v) < 0.0001, "%s, %s" % (r, v)
    return t1 - t0


ts = []
for i in xrange(1000):
    ts.append(send_ping(i))

print "times:", ts
print "\tmean: %s" % (sum(ts) / len(ts), )
print "\tmax : %s" % (max(ts), )
