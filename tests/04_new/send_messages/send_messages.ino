/*
 * A (pointless) example showing how by default the Comando class echos
 * any messages it receives.
 * Load this onto an arduino, then call the corresponding send_messages.py with python
 * You should see two messages sent to the arduino ("hi" and "how are you?") and those same
 * messages echoed back to the computer.
 */
#include<comando.h>

Comando com = Comando(Serial);
EchoProtocol echo = EchoProtocol(com);
CommandProtocol cmd = CommandProtocol(com);

void no_arg(){
  cmd.send_command(0);
};

void bool_arg(){
  cmd.start_command(1);
  cmd.add_arg((boolean) true);
  cmd.add_arg((boolean) false);
  cmd.finish_command();
};

void chr_arg(){
  cmd.start_command(2);
  cmd.add_arg('\0');
  cmd.add_arg('\r');
  cmd.add_arg('\n');
  cmd.add_arg('a');
  cmd.add_arg('Z');
  cmd.finish_command();
};

void int_arg(){
  cmd.start_command(3);
  cmd.add_arg(0L);
  cmd.add_arg(1L);
  cmd.add_arg(-1L);
  cmd.add_arg(1000000L);
  cmd.add_arg(-1000000L);
  cmd.finish_command();
};

void float_arg(){
  cmd.start_command(4);
  cmd.add_arg(0.0f);
  cmd.add_arg((float)1.0f);
  cmd.add_arg((float)-1.0f);
  cmd.add_arg((float)1.111111111f);
  cmd.add_arg((jjkfloat)-1111111111.1f);
  cmd.finish_command();
};

void setup() {
  Serial.begin(9600);
  com.register_protocol(0, echo);
  com.register_protocol(1, cmd);
  cmd.register_callback(0, no_arg);
  cmd.register_callback(1, bool_arg);
  cmd.register_callback(2, chr_arg);
  cmd.register_callback(3, int_arg);
  cmd.register_callback(4, float_arg);
}

void loop() {
  com.handle_stream();
}
