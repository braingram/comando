/*
 * 
 */
#include<comando.h>

// Initialize the comando communication stream handler
Comando com = Comando(Serial);

void echo() {
  com.send_message(com.get_bytes(), com.get_n_bytes());
};

void setup() {
  Serial.begin(9600);
  com.on_message(echo);
};

void loop() {
  com.handle_stream();
};
