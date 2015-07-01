#!/usr/bin/env python
"""
"""

import ctypes
import struct

from .base import Protocol


# type: (pack[function], unpack)
# pack/unpack: (bytes_consumed, function)
types = {
    bool: (
        lambda v: struct.pack('<?', v),
        lambda bs: (1, struct.unpack('<?', bs[0])[0])),
    chr: (
        lambda v: struct.pack('<c', v),
        lambda bs: (1, struct.unpack('<c', bs[0])[0])),
    ctypes.c_byte: (
        lambda v: struct.pack('<c', chr(v.value)),
        lambda bs: (1, struct.unpack('<c', bs[0])[0])),
    ctypes.c_char: (
        lambda v: struct.pack('<c', v),
        lambda bs: (1, struct.unpack('<c', bs[0])[0])),
    int: (
        lambda v: struct.pack('<i', v),
        lambda bs: (2, struct.unpack('<h', bs[:2])[0])),
    ctypes.c_int16: (
        lambda v: struct.pack('<h', v.value),
        lambda bs: (2, struct.unpack('<h', bs[:2])[0])),
    ctypes.c_uint16: (
        lambda v: struct.pack('<H', v.value),
        lambda bs: (2, struct.unpack('<H', bs[:2])[0])),
    ctypes.c_int32: (
        lambda v: struct.pack('<i', v.value),
        lambda bs: (4, struct.unpack('<i', bs[:4])[0])),
    ctypes.c_uint32: (
        lambda v: struct.pack('<I', v.value),
        lambda bs: (4, struct.unpack('<I', bs[:4])[0])),
    float: (
        lambda v: struct.pack('<f', v),
        lambda bs: (4, struct.unpack('<f', bs[:4])[0])),
    ctypes.c_float: (
        lambda v: struct.pack('<f', v.value),
        lambda bs: (4, struct.unpack('<f', bs[:4])[0])),
    str: (
        str,
        lambda bs: (bs[0], bs[1:1+ord(bs[0])])),
}
types[ctypes.c_bool] = types[bool]



class CommandProtocol(Protocol):
    def __init__(self, comm=None, index=0):
        self.received_arg_string = ""
        self.received_arg_string_index = 0
        self.send_arg_string = ""
        self.commands = {}
        self.callbacks = {}

    def register_callback(self, cid, func):
        self.callbacks[cid] = func

    def has_arg(self):
        return self.received_arg_string_index < len(self.received_arg_string)

    def get_arg(self, t):
        if not self.has_arg():
            return Exception("Attempt to get_arg when no arg was available")
        if t not in types:
            raise Exception("Unknown argument type: %s" % t)
        s = self.received_arg_string[self.received_arg_string_index:]
        if len(s) == 0:
            raise Exception("Received argstring is empty")
        n, v = types[t][1](s)
        #print("\t\t%s -> %s" % (map(ord, s), v))
        self.received_arg_string_index += n
        return v

    def receive_message(self, bs):
        # byte 0 = command, ....
        if len(bs) < 1:
            raise Exception("Invalid empty command message")
        self.received_arg_string = bs[1:]
        self.received_arg_string_index = 0
        cid = ord(bs[0])
        if cid in self.callbacks:
            self.callbacks[cid](self)
        else:
            raise Exception(
                "Received message for unknown command[%s]" % (cid))

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

    def finish_command(self):
        self.send_message(self.send_arg_string)
        self.send_arg_string = ""

    def send_command(self, cid, args=None):
        self.start_command(cid)
        if args is not None:
            [self.add_arg(a) for a in args]
        self.finish_command()

# TODO namespace
