
#include<comando.h>

Comando cmd = Comando(Serial);

byte n=0;
byte buffer[MAX_MSG_LENGTH];

void error() {
  cmd.send_message("oops");
};

void message() {
  n = cmd.get_bytes(buffer);
  cmd.send_message(buffer);
}

void setup() {
  Serial.begin(9600);
  cmd.on_message(message);
  cmd.on_error(error);
}

void loop() {
  cmd.handle_stream();
}
