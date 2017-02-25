#!/usr/bin/env python

import time

import serial

import pycomando

com = pycomando.Comando(serial.Serial('/dev/ttyACM0', 9600))
text = pycomando.protocols.TextProtocol(com)

com.register_protocol(0, text)


def show(text):
    print(text)

text.register_callback(show)

while True:
    com.handle_stream()
    time.sleep(0.01)
