/*
 * Time sending/receiving bytes
 */
#include<comando.h>

#define CMD_PING 0

Comando com = Comando(Serial);
TextProtocol text = TextProtocol(com);
CommandProtocol cmd = CommandProtocol(com);

float number[3] = {0., 0., 0.};

void ping(CommandProtocol *cmd) {
  number[0] = cmd->get_arg<float>();
  number[1] = cmd->get_arg<float>();
  number[2] = cmd->get_arg<float>();
  cmd->start_command(CMD_PING);
  cmd->add_arg(number[0]);
  cmd->add_arg(number[1]);
  cmd->add_arg(number[2]);
  cmd->finish_command();
};


void setup() {
  Serial.begin(115200);
  com.register_protocol(0, text);
  com.register_protocol(1, cmd);

  cmd.register_callback(CMD_PING, ping);
};

void loop() {
  com.handle_stream();
};
