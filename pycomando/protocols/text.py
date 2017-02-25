#!/usr/bin/env python

from .base import Protocol


class TextProtocol(Protocol):
    def __init__(self, comm=None, index=0):
        Protocol.__init__(self, comm, index)
        self.callbacks = []

    def register_callback(self, func):
        self.callbacks.append(func)

    def receive_message(self, bs):
        if b'\x00' in bs:
            s = bs.split('\x00')[0]
        else:
            s = bs
        for cb in self.callbacks:
            cb(s)

    def write(self, text):
        self.send_message(text)
