/*
 * A (pointless) example showing how by default the Comando class echos
 * any messages it receives.
 * Load this onto an arduino, then call the corresponding send_messages.py with python
 * You should see two messages sent to the arduino ("hi" and "how are you?") and those same
 * messages echoed back to the computer.
 */
#include<comando.h>

BaseComando cmd = BaseComando(Serial);
Commander cmder = Commander(cmd);

void a0(){
  cmd.send_message("a0");
};

void a1(){
  cmd.send_message("a1");
};

void a2(){
  cmd.send_message("a2");
};

void handle() {
  // handle message from cmd
  cmder.handle_message(cmd.get_bytes(), cmd.get_n_bytes());
};

void setup() {
  Serial.begin(9600);
  //cmd.on_message(handle);
  cmder.attach(0, a0);
  cmder.attach(1, a1);
  cmder.attach(2, a2);
}

void loop() {
  cmd.handle_stream();
}
