Command messages are built on top of protocol messages and are of the following
format:

- command id [1 byte] the identifier of the corresponding command
- payload [N bytes] the arguments to the command

When comando receives a command message, it examines the command id and then
calls the corresponding command. The called command is responsible for
parsing the payload to extract the command arguments but several helper
functions are provided.

get_arg/get_string_arg
----

This function parses the command message payload, extracts a single argument of
a provided type, and updates the payload byte counter to keep track of the
number of payload bytes remaining.

In c/Arduino, types are provided through a templated function.

```c
    // where cmd is a pointer to a CommandProtocol instance
    bool arg = cmd->get_arg<bool>();
```

The above example extracts a boolean value from the payload bytes and assigns
it to a variable, arg. The following python code does the same operation.

```python
   # where cmd is an instance of CommandProtocol
   arg = cmd.get_arg(bool)
```

It is helpful to use ctypes variables in python to gain tighter control
over the number of bits used to represent arguments. See (command.py)[https://github.com/braingram/comando/blob/master/pycomando/protocols/command.py]
for how the built-in struct module packs and unpacks various data types.

has_arg
----

This function returns a boolean value that signifies if there are any remaining
payload bytes that have not been parsed.
