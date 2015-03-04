#!/usr/bin/env python
"""
Base handler class

This is responsible for reading/writing messages
"""


def checksum(bs):
    """Compute a checksum for an array of bytes"""
    return sum([ord(b) for b in bs]) % 256


def build_message(bs):
    """Build a message around an array of bytes"""
    n = len(bs)
    if n > 255:
        raise Exception("Messages cannot contain > 255 bytes [%s]" % n)
    return chr(n) + bs + chr(checksum(bs))


class StreamHandler(object):
    def __init__(self, stream):
        self.stream = stream

    def read(self):
        n = ord(self.stream.read(1))
        if n != '\x00':
            bs = self.stream.read(n)
        else:
            bs = ""
        if len(bs) != n:
            raise Exception(
                "Invalid message length of bytes %s != %s" %
                (len(bs), n))
        cs = self.stream.read(1)
        if cs != chr(checksum(bs)):
            raise Exception(
                "Invalid message checksum [%s != %s]" %
                (chr(checksum(bs)), cs))
        self.on_message(bs)

    def write(self, bs):
        self.stream.write(build_message(bs))

    def on_message(self, bs):
        raise NotImplementedError(
            "StreamHandler does not know how to handle messages, "
            "use a differnt (subclass) handler")

    # TODO check for read, handle reads and writes?
