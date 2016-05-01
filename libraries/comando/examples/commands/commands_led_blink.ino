/*
 * Comando command protocol example
 * 2016/05/01 : Brett Graham
 * 
 * This is the follow up example that shows how to control the arduino's led blinking
 * pattern  
 * 
 * For more detailed explanation, see libraries/comando/examples/commands_led_on_off in the 
 * comando repository 
 *
 * see examples/commands_led_blink.py in the comando repository for the
 * corresponding python code
 */

#include <comando.h>


#define LED_PIN 13

unsigned long last_change = 0;
//initial state of led
byte state = 0;

// Two variables that determine the LED blinking pattern
// We define these variables below as long, 4 bytes, to match the size of the args coming
// from python.
long on_time = 1000;
long off_time = 250;

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
  
  // get_arg can be repeatly executed to grab the incoming data
  on_time = cmd->get_arg<long>();
  off_time = cmd->get_arg<long>();

  // add_arg can be repeatly executed to pack up the data
  cmd->start_command(0);
  cmd->add_arg(on_time);
  cmd->add_arg(off_time);
  cmd->finish_command();
  // after finish_command(), the data pack will be sent back to python

}

void setup() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, state);


  Serial.begin(9600);
  
  com.register_protocol(0, text);
  com.register_protocol(1, cmd);
  cmd.register_callback(0, set_led);
  
}

void loop() {
  digitalWrite(LED_PIN, HIGH);
  delay(on_time);
  // one way of utilizing millis() to enhance timing accuracy
  // prevent the error of digitalWrite and handles_stream time from
  // prolonging the LED off_time
  unsigned long t = millis();
  digitalWrite(LED_PIN, LOW);
  com.handle_stream();
  unsigned long dt = millis() - t;
  if (dt < off_time) delay(off_time - dt);


  //another way of using millis() to enhance timing accuracy

  /*
  com.handle_stream();
  unsigned long t = millis();
  if (state) {
    // pin is high
    // last state change was low to high
    if (t - last_change > on_time) {
      state = 0;
      digitalWrite(LED_PIN, state);
      last_change = t;
    }
  } else {
    // pin is low
    if (t - last_change > off_time) {
      state = 1;
      digitalWrite(LED_PIN, state);
      last_change = t;
    }
  }
  */
}
