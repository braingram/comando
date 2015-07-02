/*
 * 
 */
#include<comando.h>

// Initialize the comando communication stream handler
Comando com = Comando(Serial);
// Initialize a few communication protocols
EchoProtocol echo = EchoProtocol(com);
CommandProtocol cmd = CommandProtocol(com);

void no_arg(CommandProtocol* cmd){
  cmd->send_command(0);
};

void bool_arg(CommandProtocol* cmd){
  echo.send_message(com.get_bytes(), com.get_n_bytes());
  // send some test bools to see if they are received correctly
  cmd->start_command(1);
  if(cmd->get_arg<boolean>() == true) {
    cmd->add_arg(true);
  } else {
    cmd->add_arg(false);
  };
  if(cmd->get_arg<boolean>() == false) {
    cmd->add_arg(false);
  } else {
    cmd->add_arg(true);
  };
  cmd->finish_command();
};

void chr_arg(CommandProtocol* cmd){
  echo.send_message(com.get_bytes(), com.get_n_bytes());
  // send some test chars to see if they are received correctly
  cmd->start_command(2);
  /*
  char c = cmd.get_arg<char>();
  echo.send_message((byte *)&c, 1);
  if(c == '\r') {
    cmd.add_arg('\r');
  } else {
    cmd.add_arg('e');
  };
  */
  if(cmd->get_arg<char>() == '\r') {
    cmd->add_arg('\r');
  } else {
    cmd->add_arg('e');
  };
  if(cmd->get_arg<char>() == '\n') {
    cmd->add_arg('\n');
  } else {
    cmd->add_arg('e');
  };
  if(cmd->get_arg<char>() == 'a') {
    cmd->add_arg('a');
  } else {
    cmd->add_arg('e');
  };
  if(cmd->get_arg<char>() == 'Z') {
    cmd->add_arg('Z');
  } else {
    cmd->add_arg('e');
  };
  if(cmd->get_arg<char>() == '\0') {
    cmd->add_arg('\0');
  } else {
    cmd->add_arg('e');
  };
  cmd->finish_command();
};

void int_arg(CommandProtocol *cmd){
  echo.send_message(com.get_bytes(), com.get_n_bytes());
  // send some test ints to see if they are received correctly
  cmd->start_command(3);
  if (cmd->get_arg<long>() == 0) {
    cmd->add_arg(0L);
  } else {
    cmd->add_arg(2L);
  };
  if (cmd->get_arg<long>() == 1) {
    cmd->add_arg(1L);
  } else {
    cmd->add_arg(2L);
  };
  if (cmd->get_arg<long>() == -1) {
    cmd->add_arg(-1L);
  } else {
    cmd->add_arg(2L);
  };
  if (cmd->get_arg<long>() == 1000000) {
    cmd->add_arg(1000000L);
  } else {
    cmd->add_arg(2L);
  };
  if (cmd->get_arg<long>() == -1000000) {
    cmd->add_arg(-1000000L);
  } else {
    cmd->add_arg(2L);
  };
  cmd->finish_command();
};

void float_arg(CommandProtocol *cmd){
  echo.send_message(com.get_bytes(), com.get_n_bytes());
  // send some test floats to see if they are received correctly
  cmd->start_command(4);
  float f;
  f = cmd->get_arg<float>();
  if (abs(f - 0.0) < 0.0001) {
    cmd->add_arg(0.0f);
  } else {
    cmd->add_arg(2.0f);
  };
  f = cmd->get_arg<float>();
  if (abs(f - 1.0) < 0.0001) {
    cmd->add_arg(1.0f);
  } else {
    cmd->add_arg(2.0f);
  };
  f = cmd->get_arg<float>();
  if (abs(f + 1.0) < 0.0001) {
    cmd->add_arg(-1.0f);
  } else {
    cmd->add_arg(2.0f);
  };
  f = cmd->get_arg<float>();
  if (abs(f - 1.23) < 0.01) {
    cmd->add_arg(1.23f);
  } else {
    cmd->add_arg(2.0f);
  };
  
  f = cmd->get_arg<float>();
  if (abs(f + 123.0) < 0.01) {
    cmd->add_arg(-123.0f);
  } else {
    cmd->add_arg(2.0f);
  };
  cmd->finish_command();
};

void string_arg(CommandProtocol *cmd){
  echo.send_message(com.get_bytes(), com.get_n_bytes());
  cmd->start_command(5);
  String s;
  s = cmd->get_string_arg();
  if (s == "hi") {
    cmd->add_string_arg(String("hi"));
  } else {
    cmd->add_string_arg(s);
  };
  s = cmd->get_string_arg();
  if (s == "hello") {
    cmd->add_string_arg(String("hello"));
  } else {
    cmd->add_string_arg(s);
  };
  s = cmd->get_string_arg();
  if (s == "") {
    cmd->add_string_arg(String(""));
  } else {
    cmd->add_string_arg(s);
  };
  cmd->finish_command();
};

void setup() {
  // start stream
  Serial.begin(9600);
  // register protocols
  com.register_protocol(0, echo);
  com.register_protocol(1, cmd);
  // register command callbacks
  cmd.register_callback(0, no_arg);
  cmd.register_callback(1, bool_arg);
  cmd.register_callback(2, chr_arg);
  cmd.register_callback(3, int_arg);
  cmd.register_callback(4, float_arg);
  cmd.register_callback(5, string_arg);
}

void loop() {
  // handle streams/protocols/commands
  com.handle_stream();
}
