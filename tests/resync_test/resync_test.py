#!/usr/bin/env python

import ctypes
import sys

import pycomando
import serial

import logging

logging.basicConfig(level=logging.WARNING)
f = logging.Formatter('%(name)s[%(levelno)s]: %(message)s')
h = logging.StreamHandler()
h.setLevel(logging.INFO)
h.formatter = f
pycomando.comando.logger.addHandler(h)
pycomando.comando.logger.setLevel(logging.INFO)

port = '/dev/ttyACM1'
if len(sys.argv) > 1:
    port = sys.argv[1]

conn = serial.Serial(port, 9600)
com = pycomando.Comando(conn)
cmd = pycomando.protocols.CommandProtocol()

com.register_protocol(0, cmd)


def got_ping(cmd):
    counts = []
    while cmd.has_arg():
        counts.append(cmd.get_arg(ctypes.c_byte).value)
    print("Got ping: %s[%s]" % (counts[0], len(counts)))


def set_led(v):
    cmd.start_command(0)
    cmd.add_arg(ctypes.c_byte(v))
    cmd.finish_command()


cmd.register_callback(1, got_ping)

try:
    while True:
        try:
            i = int(raw_input(
                "Please input a value for the led (Ctrl-C to exit)"))
            set_led(i)
        except Exception as e:
            print("Invalid input: %s" % e)
        while conn.inWaiting():
            com.handle_stream()
except KeyboardInterrupt:
    conn.close()
