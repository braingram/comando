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
protocols. Let's redo the above example with two included protocols.

You can follow along with the simple example in: tests/02\_protocol

On the python side, we want to send some text to the arduino.
```python
# python
# make the protocol
text = pycomando.protocols.TextProtocol(com)
# register it with comando as protocol 0
com.register_protocol(0, text)
```

On the arduino side, we want to echo back whatever text is received.
```c
// arduino
// make the protocol
EchoProtocol echo = EchoProtocol(com);
// register it with comando as protocol 0
com.register_protocol(0, echo);
```

Notice that the protocols are different: Text in python and Echo on the arduino.
However, they were both assigned to protocol index 0 as seen in the first
argument of register_protocol. It might be helpful to think of the index as
being a communication channel. Each end of the channel can be handled differently
and each end does not know what the other end is doing. This can be useful for
a number of situations:

1. Echoing messages to check that the communication line is active and working
2. Swapping protocols from a more complicated protocol to text for debugging
3. Having a slow, development protocol and a fast production protocol
4. Setting up 1 way command passing

### Warning about register\_message\_callback

One important note is that if you register a message callback, all protocols
will be ignored!

###Assigning an error handling protocol
TODO

###Example Protocols

Here are a few example protocols included with comando.

####TextProtocol
Just sends text (byte arrays).

####EchoProtocol
Echo, send back, any received messages.

####LogProtocol
Log allows the arduino to issue python logging-like messages and python
to pass on these messages to the logging module.

####ErrorProtocol (only in python)
TODO

####CommandProtocol
Allows the arduino to call python functions and python to call arduino
functions. This is similar to the arduino cmdmessenger library.

Commands callbacks are registered in a similar way as protocols.

```python
# python
cmd = pycomando.protocols.CommandProtocol(com)
cmd.register_command(0, some_function)
cmd.register_command(1, some_other_function)
```

```c
// arduino
CommandProtocol cmd = CommandProtocol(com);
cmd.register_command(0, some_function);
cmd.register_command(1, some_other_function);
```

To call a function, send a command, use the protocol and command index, the
first argument to register_command.

```python
# python
# calls command 0 on the arduino
cmd.send_command(0)
# calls command 1 on the arduino
cmd.send_command(1)
```

```c
// arduino
// calls command 0 in python
cmd.send_command(0);
// calls command 1 in python
cmd.send_command(1);
```

In addition to calling functions, arguments can be passed between python and
the arduino.

In python, the commands must accept 1 argument, which will be the command
protocol instance. Use get\_arg to read in the arguments from the arduino.
However, you need to provide a type so the command protocol knows how to
unpack the arguments.

```python
# python
def some_function(cmd):
    arg1 = cmd.get_arg(float)
    arg2 = cmd.get_arg(int)
    arg3 = cmd.get_arg(bool)
```

A similar process is used on the arduino side.

```c
// arduino
void some_function(CommandProtocol *cmd) {
    float f = cmd->get_arg<float>();
    int i = cmd->get_arg<int>();
    bool b = cmd->get_arg<bool>();
};
```

Sending arguments follows a similar syntax.

```python
# python
# start a command, it won't be sent until finish is called
cmd.start_command(0)
# add an argument, 1.0, of type float
cmd.add_arg(1.0, float)
# add a 2nd argument, this time autodetect the type
cmd.add_arg(1)
# add a 3rd argument
cmd.add_arg(True)
# send the command
cmd.finish_command()
# this is short-hand for the same command and arguments
cmd.send_command(0, [1.0, 1, True])
```

```c
// arduino
// start a command, it won't be sent until finish is called
cmd.start_command(0);
// add an argument
cmd.add_arg(1.0);  // the type is set by the argument
// add a 2nd argument
cmd.add_arg((int)1);  // or you can cast it to a particular type
// add a 3rd argument
cmd.add_arg(true);
// send the command
cmd.finish_command();
```
