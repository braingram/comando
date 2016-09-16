#!/usr/bin/env python


class ComandoError(Exception):
    pass


class MessageError(ComandoError):
    pass


class ProtocolError(MessageError):
    pass
