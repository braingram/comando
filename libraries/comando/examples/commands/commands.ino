/*
 * Comando command protocol example
 * 2016/03/23 : Brett Graham
 * 
 * This is a simple example that shows how to control the arduino led
 * from python
 *
 * This example shows how to:
 * - send text messages from the arduino to python
 * - receive commands from python to the arduino
 * - send commands from the arduino to python
 *
 * see examples/commands.py in the comando repository for the
 * corresponding python code
 */

#include <comando.h>

#define LED_PIN 13

// Create a comando, stream handler, for the serial port
Comando com = Comando(Serial);
// Create protocols to send text and to send/receive commands
TextProtocol text = TextProtocol(com);
CommandProtocol cmd = CommandProtocol(com);

// Define a function that will be called when a command is received
void set_led(CommandProtocol *cmd) {
  // send a status message back to python
  text.print("set_led\n");

  // check if the received command has the required argument
  if (!cmd->has_arg()) {
    // if not, send a message to python
    text.print("missing argument!\n");
    // and do nothing
    return;
  }

  // read the command argument, you must define the type as
  // below to let comando know how to unpack the received argument
  byte value = cmd->get_arg<byte>();

  // write this value to the led
  digitalWrite(LED_PIN, value);

  // send a command back to python with the new led value
  // first, start building the command with the command id
  cmd->start_command(0);
  // add an argument to the command, comando will infer the type
  cmd->add_arg(value);
  // finish the command, this sends it to python
  cmd->finish_command();
}

void setup() {
  // setup the led pin
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  // start the serial connection
  Serial.begin(9600);

  // register the comando protocols
  // the first argument, the protocol id, should match on both
  // the arduino and python sides
  com.register_protocol(0, text);
  com.register_protocol(1, cmd);

  // register a callback command for a command id
  // when a '0' command is received by the arduino, the callback
  // function will be called
  cmd.register_callback(0, set_led);

  // use the text protocol to send a message to python
  text.print("Arduino is ready!\n");
}

void loop() {
  // handling the stream allows commando and the registered
  // protocols to respond to requests, this should be called
  // frequently to make a responsive system
  com.handle_stream();
}
