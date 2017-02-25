#!/usr/bin/env python

#import sys
import weakref

from .. import errors
from ..comando import to_bytes, stob

#if sys.version_info >= (3, 0):
#    stob = lambda s: s.encode('latin1') if isinstance(s, str) else s
#    btos = lambda b: b.decode('latin1') if isinstance(b, bytes) else b
#else:
#    stob = str
#    btos = str


class Protocol(object):
    """The most basic protocol that doesn't do anything"""
    def __init__(self, comm=None, index=0):
        self.index = index
        self.comm = None
        if comm is not None:
            self.assign_comm(comm)

    def assign_comm(self, comm):
        self.comm = weakref.ref(comm)

    def send_message(self, bs):
        if self.comm is None:
            raise errors.ProtocolError(
                "Protocol[%s] cannot send, no comm defined" % (self))
        comm = self.comm()
        if comm is None:
            raise errors.ProtocolError(
                "Protocol[%s] cannot send, comm has expired" % (self))
        comm.send_message(to_bytes(self.index) + stob(bs))

    def receive_message(self, bs):
        raise NotImplementedError(
            "Base Protocol does not know how to receive messages")
