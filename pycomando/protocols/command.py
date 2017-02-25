#!/usr/bin/env python
"""
"""

import ctypes
import re
import struct
import sys

from .base import Protocol
from .. import errors
from ..comando import to_bytes, stob, btos

if sys.version_info >= (3, 0):
    unicode = str

# type: (pack[function], unpack)
# pack/unpack: (bytes_consumed, function)
types = {
    bool: (
        lambda v: struct.pack('<?', v),
        lambda bs: (1, struct.unpack('<?', bs[:1])[0])),
    chr: (
        lambda v: struct.pack('<c', v),
        lambda bs: (1, struct.unpack('<c', bs[:1])[0])),
    int: (
        lambda v: struct.pack('<i', v),
        lambda bs: (4, struct.unpack('<i', bs[:4])[0])),
    float: (
        lambda v: struct.pack('<f', v),
        lambda bs: (4, struct.unpack('<f', bs[:4])[0])),
    str: (
        lambda v: to_bytes(len(v)) + stob(v),
        lambda bs: (ord(bs[:1]) + 1, btos(bs[1:1+ord(bs[:1])]))),
    bytes: (
        lambda v: to_bytes(len(v)) + v,
        lambda bs: (ord(bs[:1]) + 1, bs[1:1+ord(bs[:1])])),
    ctypes.c_byte: (
        lambda v: struct.pack('<b', v.value),
        lambda bs: (1, ctypes.c_byte(struct.unpack('<b', bs[:1])[0]))),
    ctypes.c_ubyte: (
        lambda v: struct.pack('<B', v.value),
        lambda bs: (1, ctypes.c_ubyte(struct.unpack('<B', bs[:1])[0]))),
    ctypes.c_char: (
        lambda v: struct.pack('<c', v.value),
        lambda bs: (1, ctypes.c_char(struct.unpack('<c', bs[:1])[0]))),
    ctypes.c_int16: (
        lambda v: struct.pack('<h', v.value),
        lambda bs: (2, ctypes.c_int16(struct.unpack('<h', bs[:2])[0]))),
    ctypes.c_uint16: (
        lambda v: struct.pack('<H', v.value),
        lambda bs: (2, ctypes.c_uint16(struct.unpack('<H', bs[:2])[0]))),
    ctypes.c_int32: (
        lambda v: struct.pack('<i', v.value),
        lambda bs: (4, ctypes.c_int32(struct.unpack('<i', bs[:4])[0]))),
    ctypes.c_uint32: (
        lambda v: struct.pack('<I', v.value),
        lambda bs: (4, ctypes.c_uint32(struct.unpack('<I', bs[:4])[0]))),
    ctypes.c_float: (
        lambda v: struct.pack('<f', v.value),
        lambda bs: (4, ctypes.c_float(struct.unpack('<f', bs[:4])[0]))),
}
types[ctypes.c_bool] = types[bool]


def test_type_conversion():
    c = ctypes
    tests = [
        (False, b'\x00'),
        (True, b'\x01'),  # bool
        (0, b'\x00\x00\x00\x00'),
        (1, b'\x01\x00\x00\x00'),
        (256, b'\x00\x01\x00\x00'),
        (-1, b'\xff\xff\xff\xff'),  # int
        (0.0, b'\x00\x00\x00\x00'),
        (1.0, b'\x00\x00\x80?'),
        (-1.0, b'\x00\x00\x80\xbf'),  # float
        (b'\x00', b'\x01\x00'),
        (b'\xff', b'\x01\xff'),
        ('', b'\x00'),
        ('abc', b'\x03abc'),
        (';\x00\n\r,', b'\x05;\x00\n\r,'),  # string
        (c.c_byte(0), b'\x00'),
        (c.c_byte(127), b'\x7f'),
        (c.c_byte(-128), b'\x80'),  # c_byte
        (c.c_ubyte(0), b'\x00'),
        (c.c_ubyte(127), b'\x7f'),
        (c.c_ubyte(128), b'\x80'),  # c_ubyte
        (c.c_char(b'\x00'), b'\x00'),
        (c.c_char(b'\xff'), b'\xff'),  # c_char
        (c.c_int16(0), b'\x00\x00'),
        (c.c_int16(1), b'\x01\x00'),
        (c.c_int16(-1), b'\xff\xff'),
        (c.c_int16(256), b'\x00\x01'),  # c_int16
        (c.c_uint16(0), b'\x00\x00'),
        (c.c_uint16(1), b'\x01\x00'),
        (c.c_uint16(256), b'\x00\x01'),
        (c.c_uint16(65535), b'\xff\xff'),  # c_uint16
        (c.c_int32(0), b'\x00\x00\x00\x00'),
        (c.c_int32(1), b'\x01\x00\x00\x00'),
        (c.c_int32(-1), b'\xff\xff\xff\xff'),
        (c.c_int32(256), b'\x00\x01\x00\x00'),  # c_int32
        (c.c_uint32(0), b'\x00\x00\x00\x00'),
        (c.c_uint32(1), b'\x01\x00\x00\x00'),
        (c.c_uint32(256), b'\x00\x01\x00\x00'),
        (c.c_uint32(4294967295), b'\xff\xff\xff\xff'),  # c_uint32
        (c.c_float(0.0), b'\x00\x00\x00\x00'),
        (c.c_float(1.0), b'\x00\x00\x80?'),
        (c.c_float(-1.0), b'\x00\x00\x80\xbf'),  # c_float
    ]
    for v, r in tests:
        pv = types[type(v)][0](v)
        assert pv == r, "[%s pack error] %r != %r" % (type(v), pv, r)
        uv = types[type(v)][1](r)[1]
        if hasattr(v, 'value'):
            e = uv.value == v.value
        else:
            e = uv == v
        assert e, "[%s, unpack error] %r != %r" % (type(v), uv, v)


class CommandError(errors.ProtocolError):
    pass


class CommandProtocol(Protocol):
    def __init__(self, comm=None, index=0):
        Protocol.__init__(self, comm, index)
        self.received_arg_string = ""
        self.received_arg_string_index = 0
        self.send_arg_string = bytes()
        self.callbacks = {}

    def register_callback(self, cid, func):
        self.callbacks[cid] = func

    def has_arg(self):
        return self.received_arg_string_index < len(self.received_arg_string)

    def get_arg(self, t):
        if not self.has_arg():
            raise CommandError(
                "Attempt to get_arg when no arg was available")
        if t not in types:
            raise CommandError("Unknown argument type: %s" % t)
        s = self.received_arg_string[self.received_arg_string_index:]
        if len(s) == 0:
            raise CommandError("Received argstring is empty")
        n, v = types[t][1](s)
        #print("received %r -> %s[%s]" % (s, v, n))
        self.received_arg_string_index += n
        return v

    def receive_message(self, bs):
        # byte 0 = command, ....
        #print("command.receive_message: %r" % bs)
        if len(bs) < 1:
            raise CommandError("Invalid empty command message")
        self.received_arg_string = bs[1:]
        self.received_arg_string_index = 0
        #print("Received arg string: %r" % self.received_arg_string)
        if isinstance(bs[0], int):
            cid = bs[0]
        else:
            cid = ord(bs[0])
        if cid in self.callbacks:
            self.callbacks[cid](self)
        else:
            raise CommandError(
                "Received message for unknown command[%s]" % (cid))

    def start_command(self, cid):
        if len(self.send_arg_string) != 0:
            raise CommandError(
                "Cannot start new command [%s], command already started [%s]" %
                (cid, self.send_arg_string))
        self.send_arg_string += to_bytes(cid)

    def add_arg(self, v, t=None):
        if t is None:
            t = type(v)
        if t not in types:
            raise CommandError("Unknown argument type: %s" % t)
        self.send_arg_string += bytes(types[t][0](v))

    def finish_command(self):
        self.send_message(self.send_arg_string)
        self.send_arg_string = bytes()

    def send_command(self, cid, args=None):
        self.start_command(cid)
        if args is not None:
            [self.add_arg(a) for a in args]
        self.finish_command()


def from_ctypes(*values):
    return [getattr(v, 'value', v) for v in values]


def attribute_function(mgr, cmd, return_ctypes=False):
    # build attribute by name
    if 'result' in cmd:
        nr = len(cmd['result'])
        if nr == 1:
            if return_ctypes:
                def afunc(*args):
                    return mgr.blocking_trigger(cmd['name'], *args)[0]
            else:
                def afunc(*args):
                    return from_ctypes(
                        *mgr.blocking_trigger(cmd['name'], *args))[0]
        else:
            if return_ctypes:
                def afunc(*args):
                    return mgr.blocking_trigger(cmd['name'], *args)
            else:
                def afunc(*args):
                    return from_ctypes(
                        *mgr.blocking_trigger(cmd['name'], *args))
    else:
        def afunc(*args):
            return mgr.trigger(cmd['name'], *args)
    # build doc string
    ds = ""
    if 'args' in cmd:
        ds += "args: %s" % (cmd['args'], )
    else:
        ds += "no arguments"
    if 'result' in cmd:
        ds += "\nresults: %s" % (cmd['result'], )
    if 'doc' in cmd:
        ds += "\n%s" % (cmd['doc'], )
    afunc.__doc__ = ds
    return afunc


class Namespace(object):
    def __init__(self, manager, return_ctypes=False):
        self._mgr = manager
        # build namespace
        cmds = self._mgr._commands
        for ci in cmds:
            cmd = cmds[ci]
            setattr(
                self, cmd['name'], attribute_function(
                    self._mgr, cmd, return_ctypes=return_ctypes))


def resolve_ctypes_type(t):
    if isinstance(t, (str, unicode)):
        t = t.strip()
        if hasattr(ctypes, t):
            return getattr(ctypes, t)
        if hasattr(ctypes, 'c_' + t):
            return getattr(ctypes, 'c_' + t)
        raise CommandError("Invalid type (not in ctypes): %s" % t)
    return t

cid_regex = r"(?P<id>\d*:)(?P<cmd>.*)"
command_regex = r"(?P<name>[\w\s]*)(?P<args>[\\(\w,\s\\)]*)?(?P<result>=[\w,\s]*)?(?P<doc>\?.*)?"


def resolve_command_types(commands):
    """
    Resolve a command definition

    Command definitions can be dictionaries or strings. This function will:
    - convert command strings to dictionaries
    - resolve ctypes datatypes from strings ("byte" becomes ctypes.c_byte)

    Command strings should take the form:
        id:name(arg0,arg1)=result?doc

    id and name are required, the rest are optional

    See EventManager for a description of the resulting command structure.
    """
    # id:name(arg0,arg1)=result?doc
    if isinstance(commands, (str, unicode)):
        cd = {}
        for cs in commands.splitlines():
            s = cs.strip()
            if len(s) and s[0] != '#':
                m = re.match(cid_regex, s)
                if m is None:
                    raise CommandError("Invalid command def: %s" % s)
                cid = int(m.group('id')[:-1])
                cd[cid] = m.group('cmd')
        commands = cd
    for cid in commands:
        command = commands[cid]
        if isinstance(command, (str, unicode)):
            #print(command)
            m = re.match(command_regex, command.strip())
            if m is None:
                raise CommandError(
                    "Invalid command def[%s]: %s" % (cid, command))
            command = {'name': m.group('name').strip()}
            gd = m.groupdict()
            if gd['args'] is not None and len(gd['args']):
                command['args'] = m.group('args')[1:-1]
            if gd['doc'] is not None and len(gd['doc']):
                command['doc'] = m.group('doc')[1:]
            if gd['result'] is not None and len(gd['result']):
                command['result'] = m.group('result')[1:]
            #print(command)
        if 'args' in command:
            if isinstance(command['args'], (str, unicode)):
                command['args'] = command['args'].split(',')
            if not isinstance(command['args'], (tuple, list)):
                command['args'] = (command['args'], )
            # resolve args
            command['args'] = [resolve_ctypes_type(t) for t in command['args']]
        if 'result' in command:
            if isinstance(command['result'], (str, unicode)):
                command['result'] = command['result'].split(',')
            if not isinstance(command['result'], (tuple, list)):
                command['result'] = (command['result'], )
            # resolve result
            command['result'] = [
                resolve_ctypes_type(t) for t in command['result']]
        commands[cid] = command
    return commands


class EventManager(object):
    def __init__(self, command_protocol, commands):
        """
        An event-driven interface to a command protocol stream.

        command_protocol = CommandProtocol instance
        commands = dict of:
            keys = command_id
            values = dicts with:
                'name': unique command name as a string
                'args': command argument types (used for trigger/send)
                'result': command result types (used for on/receive)
                'doc': command doc string

        This class allows name-based access to commands and proves
        both asynchronous (trigger, on) and synchronous (blocking_trigger)
        methods to communicate on the command protocol stream.
        """
        self._commands = resolve_command_types(commands)
        self._commands_by_name = {}
        for cid in self._commands:
            command = self._commands[cid]
            if 'name' not in command:
                raise ValueError("Command must have name: %s" % (command, ))
            n = command['name']
            if 'name' in self._commands_by_name:
                raise ValueError("Command name %s is not unique" % (n, ))
            command['id'] = cid
            self._commands_by_name[n] = command
        self._cmd = command_protocol
        for cid in self._commands:
            self._cmd.register_callback(
                cid,
                lambda cmd, cid=cid: self._receive_event(cmd, cid))
        self._callbacks = {}
        self._wait_for = None

    def _receive_event(self, cmd, cid):
        if cid not in self._commands:
            raise ValueError("Received unknown command with index=%s" % cid)
        command = self._commands[cid]
        # unpack results
        if 'result' in command:
            result_spec = command['result']
            result = []
            for spec in result_spec:
                if not cmd.has_arg():
                    continue
                    # raise ValueError(
                    #     "Not enough [%s] arguments to unpack the result [%s]"
                    #     % (len(result), len(result_spec)))
                result.append(cmd.get_arg(spec))
        else:
            result = []
        return self._handle_event(command['name'], result)

    def _handle_event(self, name, result):
        if name in self._callbacks:
            [cb(*result) for cb in self._callbacks[name]]
        if name == self._wait_for:
            self._wait_for = result

    def on(self, name, func):
        """Register a callback (func) for a given command name"""
        if name not in self._callbacks:
            self._callbacks[name] = []
        self._callbacks[name].append(func)

    def trigger(self, name, *args):
        """Trigger a command by name with arguments (args)"""
        # find command by name
        if name not in self._commands_by_name:
            raise ValueError("Unknown command name: %s" % (name, ))
        command = self._commands_by_name[name]
        cid = command['id']
        if 'args' not in command or len(args) == 0:
            return self._cmd.send_command(cid)
        arg_spec = command['args']
        # accept < args then arg_spec
        if len(args) > len(arg_spec):
            raise ValueError(
                "len(args)[%s] > len(arg spec)[%s] for command %s" %
                (len(args), len(arg_spec), name))
        na = len(args)
        pargs = [s(a) for (s, a) in zip(arg_spec[:na], args[:na])]
        self._cmd.send_command(cid, pargs)

    def blocking_trigger(self, name, *args):
        """Trigger a command and wait for a response with the same name"""
        if self._wait_for is not None:
            raise ValueError(
                "Unexpected _wait_for is not None %s" % (self._wait_for, ))
        self.trigger(name, *args)
        self._wait_for = name
        comm = self._cmd.comm()
        error = None
        while (self._wait_for is name) and (error is None):
            try:
                comm.handle_stream()
            except (Exception, KeyboardInterrupt) as e:
                error = e
        del comm
        r = self._wait_for
        self._wait_for = None
        if error is not None:
            raise e
        return r

    def build_namespace(self, return_ctypes=False):
        return Namespace(self, return_ctypes=return_ctypes)
