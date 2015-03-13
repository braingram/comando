/* A very simple comando example
 * This does NOT use protocols and in that way is a BAD example
 */
#include<comando.h>

// Initialize the comando communication stream handler
Comando com = Comando(Serial);
// setup and Echo protocol, this just sends back whatever is received
EchoProtocol echo = EchoProtocol(com);

void setup() {
  // start up the serial port
  Serial.begin(9600);
  // register the echo protocol
  com.register_protocol(0, echo);
};

void loop() {
  // handle the incoming messages
  com.handle_stream();
};
