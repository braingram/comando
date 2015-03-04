A (working) alternative to cmdmessenger.

Message format: length in bytes 0-255,byte0,byte1...byteN-1,checksum

No lf, no cr, no nothing

This is the simplest form of the message.
On top of this, a cmdmessenger-like protocol is defined.

Message format: cmd 0-255,args...

Each command will have to know prior to execution:

# how many args to expect [if any]
# the types of each arg

Args could be any type (strings, ints, bools, floats, etc...).

An alternative (keeping with the length,blah) would be

Message format: cmd 0-255,nargs 0-255,arg0...argn-1 where each arg is

Arg format: argtype 0-255,argbyte0...argbyte-1

A fancier alternative would be to allow for different protocols. With
some being more verbose than others (to allow for easier debugging).

Message format: protocol 0-255,...

With 1 protocol being

cmd 0-255,nargs 0-255,args as strings

and another being

cmd 0-255,nargs 0-255, args as packed bytes

This way, verbose and more concise (but less readable) protocols can easily be swapped.

#Message format
##Basic
A completely unprocessed command

msglength(0-255),byte0,byte1...byteN-1,checksum

where checksum is a sum of all bytes (not message length) % 256

Everything else is built on top of this by packing stuff into the bytes payload.

##Payload

The first byte of the payload defines the protocol to use: protocol[0-255]
Everything after this is defined by the protocol

#Protocols
##Command (similar to cmdmessenger)
Format:
    cmd(0-255),arg0byte0,arg1byte1...

###argtypes

Name (index): nbytes, format
- boolean (0): 1
- char (1): 1
- uchar (2): 1
- byte (3): 1
- int (4): 2
- uint (5): 2
- long (6): 4
- ulong (7): 4
- float (8): 4
- string (9): var, len(0-255),byte0,byte1...byteN-1

The benefit of multiple protocols is that I can do things like this

- issue a command (protocol 1: ...)
- receive debug feedback (protocol 0: ...)
- receive error messages (protocol 0: ...)
- control individual pins (protocol 2: ...)

This could also be done by connecting particular commands. So maybe a command of commands (this is tricky).

protocol (on arduino) should have:

- unpack: unpack a message from bytes
- pack: pack a message into bytes
- receive: receive message from computer
- send: send message to computer


So far things are shaping up as having 1 command passing structure (Comando).
This can have several protocols (for plain text, packed commands, errors, etc). Format is as follows

length in bytes (0-255), payload (...), checksum (1 byte)

payload has:

protocol index (0-255), protocol payload

Some protocols include:

Text protocol (0): just send/receive
Echo protocol (1): echos everything received
Error protocol (2): todo
Command protocol (3): todo, similar to cmdmessenger
