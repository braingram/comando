#!/usr/bin/env python

from .base import Protocol


class TextProtocol(Protocol):
    def receive_message(self, bs):
        pass

    def write(self, text):
        self.send_message(text)
