#!/usr/bin/env python
# Comando command protocol example
# 2016/05/01 : Brett Graham
#
# This is the follow up example that shows how to control the Arduino led
# blinking pattern by sending and receiving commands with multiple arguments
#
#
# see libraries/comando/examples/led_blink in the
# comando repository for the corresponding arduino code
#
# for more detailed explanation, go to examples/led_on_off.py
# in to comando repository

import sys
import time

import pycomando
import serial

if len(sys.argv) < 2:
    raise Exception("A serial port must be supplied: commands.py <port>")
port = sys.argv[1]

serial_port = serial.Serial(port, 9600)

com = pycomando.Comando(serial_port)
text = pycomando.protocols.TextProtocol(com)
cmd = pycomando.protocols.CommandProtocol(com)


com.register_protocol(0, text)
com.register_protocol(1, cmd)


def print_message(msg):
    print("from arduino->%s" % msg)


#  get_arg and has_arg can be repeatedly executed to grab incoming data
#  as many times as you like
def led_set(cmd):
    # if no data is received, raise an error
    if not cmd.has_arg():
        raise Exception("Invalid led_set response, missing both arg")
    # grab the first piece of data
    v = cmd.get_arg(int)
    # print out the number
    print("Led on time was set to: %s ms" % v)
    # check if the second argument is missing
    if not cmd.has_arg():
        raise Exception("missing the 2nd arg")
    # if not, grab the second piece of data
    b = cmd.get_arg(int)
    # print out the number
    print("Led off time was set to: %s ms" % b)


text.receive_message = print_message

cmd.register_callback(0, led_set)



try:
    while True:
        try:
            # input as first argument
            i = int(raw_input(
                "Please input a value for the led ontime (ms): " ))
            # input as second argument
            b = int(raw_input(
                "please input a value for the led offtime (ms): "))
            # send_command iterates through the list of arguments, and
            # sends the arguments one at a time
            cmd.send_command(0, [i,b])

        except Exception as e:
            print("Invalid input: %s" % e)

        time.sleep(0.1)
        try:
            while serial_port.inWaiting():
                com.handle_stream()
        except Exception as e:
            print("%s" % e)
except KeyboardInterrupt:
    serial_port.close()
