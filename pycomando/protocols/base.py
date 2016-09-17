#!/usr/bin/env python

import weakref

from .. import errors


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
        comm.send_message(chr(self.index) + bs)

    def receive_message(self, bs):
        raise NotImplementedError(
            "Base Protocol does not know how to receive messages")
