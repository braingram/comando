Comando... Command your arduino!

## Inspiration

How many times have you written a 'simple' protocol for communicating with
an Arduino that turned into anything but 'simple'? This project is meant to
solve a few goals

1. make calling commands on an arduino from a computer (and vice versa) easy
2. remove the need to write serial protocols for transferring common datatypes
3. allow simultaneuous use of multiple protocols (e.g. debug and command)

The initial inspiration came from an attempt to use cmdmessenger and finding
it difficult to send simple datatypes (i.e. floats).


## Install

To install the python library run

```
python setup.py install
```

To install the arduino library, copy libraries/comando to wherever your
arduino libraries are located (~/sketchbook/libraries on linux).

## Overview

You have two devices: 1 running python, and an arduino. You want these to:

1. call commands on the other one
2. transfer data

This communication happens over a stream (e.g. serial port), and will follow
some structure (a protocol) that defines how data (i.e. messages) are
organized. This structure is mirrored in comando.

## Streams

A stream is the conduit through which messages are passed between python and
the arduino. So far, this is a serial port but could be anything that allows
passing bytes back and forth (i.e. has read, write).

## Protocols

The real power of comando comes with using protocols. Protocols are ways to
structure messages to do things like:

1. have python trigger commands on the arduino
2. have the arduino trigger commands in python

To use protocols, create a stream and handler (as above). Then register some
protocols. Some example protocols are below.

####TextProtocol
Just sends text (byte arrays).

####LogProtocol
Log allows the arduino to issue python logging-like messages and python
to pass on these messages to the logging module.

####CommandProtocol
Allows the arduino to call python functions and python to call arduino
functions. This is similar to the arduino cmdmessenger library.

Commands callbacks are registered in a similar way as protocols.

### Warning about register\_message\_callback

One important note is that if you register a message callback with the handler,
all protocols will be ignored!

## Example

see examples/commands.py for a basic example
