/*
 * Try to cause resyncing errors and recover from them
 */

#include <comando.h>

#define CMD_LED 0
#define CMD_PING 1

#define LED_PIN 13

#define PING_DELAY 100

Comando com = Comando(Serial);

CommandProtocol cmd = CommandProtocol(com);

byte ping_count = 0;
unsigned int last_ping = 0;


void set_led(CommandProtocol *cmd) {
  if (!cmd->has_arg()) {
    return;
  }
  byte value = cmd->get_arg<byte>();
  digitalWrite(LED_PIN, value);
}


void send_ping() {
  cmd.start_command(CMD_PING);
  for (byte i=0; i < 10; i++) {
    cmd.add_arg(ping_count + i);
  };
  cmd.finish_command();
  ping_count++;
}


void setup() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  Serial.begin(9600);

  com.register_protocol(0, cmd);

  cmd.register_callback(CMD_LED, set_led);
};


void loop() {
  com.handle_stream();
  if (millis() - last_ping >= PING_DELAY) {
    send_ping();
    last_ping = millis();
  };
};

