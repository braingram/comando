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

You can follow along with the simple example in: tests/01\_simple

```python
# python
# create and setup the device you will use for communication
port = serial.Serial('/dev/ttyACM0', 9600)
# create a handler for this device/stream
com = pycomando.Comando(port)
```

```c
// arduino
// create the communication device
Serial.begin(9600);
// create a handler for this device/stream
Comando com = Comando(Serial);
```

These stream handles can send/receive messages. However it's probably better
to use a protocol!

```python
# python
# send a message to the arduino
com.send_message("hi!")


def show(bytes):
    print(bytes)


# just print out received messages
com.register_message_callback(show)
```

```c
// arduino
// send a message to python
com.send_message("hi");


void show() {
  // send the message back to python
  com.send_message(com.get_bytes(), com.get_n_bytes());

// call show when a message is received
com.register_message_callback(show);
```

For messages to be sent/recieved, the device has to have a chance to "handle"
the stream.

```python
# python
com.handle_stream()
```

```c
// arduino
com.handle_stream();
```

## Protocols

The real power of comando comes with using protocols. Protocols are ways to
structure messages to do things like:

1. have python trigger commands on the arduino
2. have the arduino trigger commands in python

To use protocols, create a stream and handler (as above). Then register some
protocols.

```python
# python
com.register_protocol(0, error)
com.register_protocol(1, text)
com.register_protocol(2, echo)
com.register_protocol(3, log)
com.register_protocol(4, command)
```

```c
// arduino
com.register_protocol(0, error)
com.register_protocol(1, echo)
com.register_protocol(2, text) // notice the swap of text and echo
com.register_protocol(3, log)
com.register_protocol(4, command)
```

## Messages
