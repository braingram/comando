#!/usr/bin/env python

from .base import Protocol
from .. import errors

import logging

log = logging.getLogger(__name__)


class ErrorProtocol(Protocol):
    def receive_message(self, bs):
        log.error(bs)
        raise errors.ProtocolError(bs)
