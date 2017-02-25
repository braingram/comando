#!/usr/bin/env python
# Comando namespace example
# 2017/02/25 : Brett Graham
#
# This example shows how to use a Namespace to control the arduino led
# from python

# ctypes is useful for defining fixed size data types
import ctypes
import sys
import time

import pycomando
import serial

if len(sys.argv) < 2:
    raise Exception("A serial port must be supplied: commands.py <port>")
port = sys.argv[1]

# open the serial port
serial_port = serial.Serial(port, 9600)

# create comando, the stream handler
com = pycomando.Comando(serial_port)
# create a few protocols to receive text and send/receive commands
text = pycomando.protocols.TextProtocol(com)
cmd = pycomando.protocols.CommandProtocol(com)

# register the created protocols, the protocol ids (first argument)
# should match on both the arduino and in python
com.register_protocol(0, text)
com.register_protocol(1, cmd)


# define a callback to be used for the text protocol
def print_message(msg):
    # just print out the message with a header
    print("from arduino->%s" % msg)


# tell the text protocol what function to call when a message is received
text.receive_message = print_message


# define the commands on the command protocol
commands = {
    0: {
        'name': 'led_set',
        'args': (ctypes.c_byte, ),
        'result': (ctypes.c_byte, ),
    }
}

# construct an event manager to allow easier access to the commands
mgr = pycomando.protocols.command.EventManager(cmd, commands)
ns = mgr.build_namespace()

print("Set to 1: %s" % ns.led_set(1))
time.sleep(1)
print("Set to 0: %s" % ns.led_set(0))
serial_port.close()
