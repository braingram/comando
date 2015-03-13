#!/usr/bin/env python

from .base import Protocol

import logging


class LogProtocol(Protocol):
    def __init__(self, comm=None, index=0, logger=None):
        Protocol.__init__(self, comm, index)
        self.logger = None
        if logger is not None:
            self.assign_logger(logger)
        else:
            self.logger = logging.getLogger(__name__)

    def assign_logger(self, logger):
        self.logger = logger

    def receive_message(self, bs):
        if len(bs) < 1:
            self.logger.error("Received empty log message")
        self.logger.log(bs[0], bs[1:])

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
