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


class Comando(object):
    def __init__(self, stream, protocols=None):
        self.stream = stream
        self.protocols = {}
        self.message_callback = None
        self.error_protocol = -1
        if protocols is not None:
            [self.register_protocol(i, p) for (i, p) in enumerate(protocols)]

    def _resync(self, chars):
        # first see if there is a valid message inside these chars
        for (i, c) in enumerate(chars):
            n = ord(c)
            e = i + 1 + n
            if e >= len(chars):
                continue
            bs = chars[i+1:e]
            cs = chars[e]
            if chr(checksum(bs)) == cs:
                # this is a valid message, so parse it and keep trying to sync
                self.receive_message(bs)
                if e + 1 >= len(chars):  # we're in sync!
                    return
                return self._resync(chars[e+1:])
        # no sync found, read 1 more char
        return self._resync(chars + self.stream.read(1))

    def handle_stream(self, poll=True):
        if poll and hasattr(self.stream, 'inWaiting'):
            while self.stream.inWaiting():
                self.handle_stream(poll=False)
            return
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
            # this may be a result of out-of-sync communication
            # TODO find a way to recover from this
            # original data was:
            #  chr(n) + bs + cs
            return self._resync(chr(n) + bs + cs)
            raise Exception(
                "Invalid message checksum [%s != %s]" %
                (chr(checksum(bs)), cs))
        self.receive_message(bs)

    def register_protocol(self, index, protocol):
        self.protocols[index] = protocol
        protocol.assign_comm(self)
        protocol.index = index

    def set_error_protocol(self, pid):
        self.error_protocol = pid

    def register_message_callback(self, f):
        self.message_callback = f

    def unregister_message_callback(self, f):
        self.message_callback = None

    def send_error(self, bs):
        if self.error_protocol != -1:
            self.protocols[self.error_protocol].send_message(bs)

    def send_message(self, bs):
        self.stream.write(build_message(bs))

    def receive_message(self, bs):
        if self.message_callback is not None:
            return self.message_callback(bs)
        if (len(bs) < 1):
            raise Exception("Invalid message, missing protocol")
        pid = ord(bs[0])
        if pid not in self.protocols:
            raise Exception("Unknown protocol: %s" % pid)
        self.protocols[pid].receive_message(bs[1:])
