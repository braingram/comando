#!/usr/bin/env python

from .base import Protocol

import logging

log = logging.getLogger(__name__)


class LogProtocol(Protocol):
    def receive_message(self, bs):
        if len(bs) < 1:
            log.error("Received empty log message")
        log.log(bs[0], bs[1:])

    def log(self, level, message):
        self.send_message(chr(level) + message)

    def debug(self, message):
        self.log(logging.DEBUG, message)

    def info(self, message):
        self.log(logging.INFO, message)

    def warn(self, message):
        self.log(logging.WARN, message)

    def warning(self, message):
        self.log(logging.WARNING, message)

    def error(self, message):
        self.log(logging.ERROR, message)

    def critical(self, message):
        self.log(logging.CRITICAL, message)

    def fatal(self, message):
        self.log(logging.FATAL, message)
