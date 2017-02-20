#!/usr/bin/env python
# Comando event manager example
# 2016/07/22 : Brett Graham
#
# This example shows how to use an EventManager to control the arduino led
# from python

# ctypes is useful for defining fixed size data types
import ctypes
import sys

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


# define a callback that will be called when the arduino sends
# a specific command to python
def led_set(v):
    print("Led was set to value: %s" % v)


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

# register the callback "led_set" to be called whenever the arduino
# sends a led_set command to python
mgr.on('led_set', led_set)

# send an initial (blocking) command to the arduino to turn off the led
mgr.blocking_trigger('led_set', 0)

# this code below reads input from the user and sets the led value
# to that input and updates comando to handle any incoming messages
# from the arduino
try:
    while True:
        try:
            # read the user input
            i = int(input(
                "Please input a value for the led (Ctrl-C to exit)"))
            # send the input to the arduino (asynchronously)
            mgr.trigger('led_set', i)
        except Exception as e:
            print("Invalid input: %s" % e)
        # update comando
        while serial_port.inWaiting():
            com.handle_stream()
except KeyboardInterrupt:
    # finally, close the serial port and exit
    serial_port.close()
