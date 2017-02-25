#!/usr/bin/env python
"""
Base handler class

This is responsible for reading/writing messages
"""

import logging
import sys

from . import errors


if sys.version_info >= (3, 0):
    to_bytes = lambda i: i.to_bytes(1, 'little')
    stob = lambda s: s.encode('latin1') if isinstance(s, str) else s
    btos = lambda b: b.decode('latin1') if isinstance(b, bytes) else b
else:
    to_bytes = chr
    stob = str
    btos = str

logger = logging.getLogger(__name__)


if False:  # set to True for debugging
    logger.setLevel(logging.DEBUG)
    f = logging.Formatter(
        '%(name)s[%(levelno)s]: %(message)s')
    h = logging.StreamHandler()
    h.formatter = f
    logger.addHandler(logging.StreamHandler())


def checksum(bs):
    """Compute a checksum for an array of bytes"""
    if len(bs) == 0:
        return 0
    if isinstance(bs[0], int):
        return sum(bs) % 256
    else:
        return sum([ord(b) for b in bs]) % 256


def build_message(bs):
    """Build a message around an array of bytes"""
    n = len(bs)
    if n > 255:
        raise errors.MessageError(
            "Messages cannot contain > 255 bytes [%s]" % n)
    return bytes(to_bytes(n) + stob(bs) + to_bytes(checksum(bs)))


class Comando(object):
    def __init__(self, stream, protocols=None):
        self.stream = stream
        self.protocols = {}
        self.message_callback = None
        self.error_protocol = -1
        if protocols is not None:
            [self.register_protocol(i, p) for (i, p) in enumerate(protocols)]

    def _resync(self, chars):
        logging.warning("resyncing")
        #logger.warning("resyncing")
        # first see if there is a valid message inside these chars
        for (i, c) in enumerate(chars):
            n = ord(c)
            e = i + 1 + n
            if e >= len(chars):
                continue
            bs = chars[i+1:e]
            cs = chars[e]
            if to_bytes(checksum(bs)) == cs:
                # this is a valid message, so parse it and keep trying to sync
                try:
                    self.receive_message(bs)
                except errors.ComandoError as err:
                    logging.warning("resyncing on message error: %s" % err)
                    return self._resync(chars[e+1:])
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
        #if n != '\x00':
        if n != 0:
            bs = self.stream.read(n)
        else:
            bs = ""
        if len(bs) != n:
            raise errors.MessageError(
                "Invalid message length of bytes %s != %s" %
                (len(bs), n))
        cs = self.stream.read(1)
        if cs != to_bytes(checksum(bs)):
            logger.warning(
                "checksum did not match: %s, %s", cs, to_bytes(checksum(bs)))
            # this may be a result of out-of-sync communication
            # recover from this
            # original data was:
            #  to_bytes(n) + bs + cs
            return self._resync(to_bytes(n) + bs + cs)
            #raise Exception(
            #    "Invalid message checksum [%s != %s]" %
            #    (to_bytes(checksum(bs)), cs))
        self.receive_message(bs)

    def register_protocol(self, index, protocol):
        logger.info("register_protocol[%s] at index: %s", protocol, index)
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
        logger.debug("send_message: %r", bs)
        self.stream.write(build_message(bs))

    def receive_message(self, bs):
        logger.debug("receive_message: %r", bs)
        if self.message_callback is not None:
            return self.message_callback(bs)
        if (len(bs) < 1):
            raise errors.MessageError("Invalid message, missing protocol")
        if isinstance(bs[0], int):
            pid = bs[0]
        else:
            pid = ord(bs[0])
        if pid not in self.protocols:
            raise errors.MessageError("Unknown protocol: %s" % pid)
        self.protocols[pid].receive_message(bs[1:])
