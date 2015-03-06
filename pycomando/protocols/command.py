#!/usr/bin/env python
"""
bool
char
uchar
byte
int16
uint16
int32
uint32
float
char
string
"""

import ctypes
import struct

from .base import Protocol


# type: (pack[function], unpack)
# pack/unpack: (bytes_consumed, function)
types = {
    bool: (chr, lambda bs: (1, chr(bs[0]))),
    chr: (chr, lambda bs: (1, bs[0])),
    ctypes.c_int16: (
        lambda v: struct.pack('<h', v),
        lambda bs: (2, struct.unpack('<h', bs[:2]))),
    ctypes.c_uint16: (
        lambda v: struct.pack('<H', v),
        lambda bs: (2, struct.unpack('<H', bs[:2]))),
    ctypes.c_int32: (
        lambda v: struct.pack('<i', v),
        lambda bs: (4, struct.unpack('<i', bs[:2]))),
    ctypes.c_uint32: (
        lambda v: struct.pack('<I', v),
        lambda bs: (4, struct.unpack('<I', bs[:2]))),
    float: (
        lambda v: struct.pack('<f', v),
        lambda bs: (4, struct.unpack('<f', bs[:2]))),
    str: (
        str,
        lambda bs: (bs[0], bs[1:1+ord(bs[0])])),
}
types[int] = types[ctypes.c_int32]
types[ctypes.c_bool] = types[bool]
types[ctypes.c_char] = types[chr]
types[ctypes.c_byte] = types[chr]
types[ctypes.c_float] = types[float]


class CommandProtocol(Protocol):
    def __init__(self, comm=None, index=0):
        self.received_arg_string = ""
        self.received_arg_string_index = 0
        self.send_arg_string = ""
        self.commands = {}

    def get_arg(self, t):
        if t not in types:
            raise Exception("Unknown argument type: %s" % t)
        s = self.received_arg_string[self.received_arg_string_index:]
        if len(s) == 0:
            raise Exception("Received argstring is empty")
        n, v = types[t][1](s)
        self.received_arg_string_index += n
        return v

    def add_command(self, cid, function):
        self.commands[cid] = function

    def receive_message(self, bs):
        # byte 0 = command, ....
        if len(bs) < 1:
            raise Exception("Invalid empty command message")
        self.received_arg_string = bs[1:]
        self.received_arg_string_index = 0
        self.commands[ord(bs[0])](self)

    def start_command(self, cid):
        if len(self.send_arg_string) != 0:
            raise Exception(
                "Cannot start new command [%s], command already started [%s]" %
                (cid, self.send_arg_string))
        self.send_arg_string += chr(cid)

    def add_arg(self, v, t=None):
        if t is None:
            t = type(v)
        if t not in types:
            raise Exception("Unknown argument type: %s" % t)
        self.send_arg_string += types[t][0](v)

    def send_command(self, cid=None, args=None):
        if cid is not None:
            self.start_command(cid)
        if args is not None:
            [self.add_arg(a) for a in args]
        self.send_message(self.send_arg_string)
        self.send_arg_string = ""

# TODO namespace
