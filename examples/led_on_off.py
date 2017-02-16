#!/usr/bin/env python
# Comando command protocol example
# 2016/05/01 : Brett Graham
#
# This is a simple example that shows how to control the arduino led
# from python
#
# This example shows how to:
# - receive text messages from the arduino
# - send commands with single arguemnt from python to the arduino
# - receive commands from the arduino in python
#
# see libraries/comando/examples/led_on_off in the comando repository
# for the corresponding arduino code
#
# after this example, check out led_blink.py for how to handle give
# commands with multiple arguments


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

# create comando instance, the stream handler
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


# define a callback that will be called when the arduino sends
# a specific command to python
def led_set(cmd):
    # first, check if the command contained any arguments
    if not cmd.has_arg():
        # if not, throw an error
        raise Exception("Invalid led_set response, missing arg")
    # read the argument, you must tell comando the data type so
    # it knows how many bytes to unpack, this is where it is
    # helpful to use ctypes data types rather than the usual
    # python types as they are of a fixed size
    v = cmd.get_arg(ctypes.c_byte)
    print("Led was set to value: %s" % v)

# tell the text protocol what function to call when a message is received
text.receive_message = print_message

# register the callback "led_set" to be called whenever the arduino
# sends a command of "0" to python
cmd.register_callback(0, led_set)

# send an initial command to the arduino to turn off the led
cmd.send_command(0, (ctypes.c_byte(0), ))
print("waiting for initial command to finish")
# The delay allows arduino to repsond properly
# comment the next 2 lines to see the difference
time.sleep(0.1)
com.handle_stream()

# this code below reads input from the user and sets the led value
# to that input and updates comando to handle any incoming messages
# from the arduino
try:
    while True:
        try:
            # read the user input
            i = int(raw_input(
                "Please input a value for the led (Ctrl-C to exit)"))
            # send the input to the arduino, notice the command id
            # and that the second argument is a tuple (or could be any iterator
            cmd.send_command(0, (ctypes.c_byte(i), ))
        except Exception as e:
            print("Invalid input: %s" % e)
        # the delay allows arduino to respond properly
        # comment the next line to see the difference
        time.sleep(0.1)
        # update comando
        while serial_port.inWaiting():
            com.handle_stream()
except KeyboardInterrupt:
    # finally, close the serial port and exit
    serial_port.close()
