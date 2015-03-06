#!/usr/bin/env python

from .base import Protocol


class EchoProtocol(Protocol):
    def receive_message(self, bs):
        self.send_message(bs)
