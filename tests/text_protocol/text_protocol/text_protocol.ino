/* A very simple comando example
 * This does NOT use protocols and in that way is a BAD example
 */
#include<comando.h>

// Initialize the comando communication stream handler
Comando com = Comando(Serial);
// create a text protocol for sending plain text
TextProtocol text = TextProtocol(com);

void setup() {
  // start up the serial port
  Serial.begin(9600);
  // register the text protocol
  com.register_protocol(0, text);
};

void loop() {
  text.print("Hello World!");
  // handle the incoming messages
  com.handle_stream();
  delay(1000);
};
