#include <comando.h>

byte compute_checksum(byte *bytes, byte n) {
    byte cs = 0;
    for (byte i=0; i<n; i++) cs += bytes[i];
    return cs;
};

void BaseComando::handle_byte(byte b) {
  if (read_state == WAITING) {
    // this is n
    n_bytes = b;
    byte_index = 0;
    read_state = READING;
  } else {  // READING
    if (byte_index == n_bytes) {  // b = checksum
      byte_index = 0; // reset byte_index for reading
      cs = b;
      if (cs != compute_checksum(bytes, n_bytes)) {
        if (error_callback != NULL) {
          (*error_callback)();
        } else {
          default_error_callback();
        };
      } else {
        if (message_callback != NULL) {
          (*message_callback)();
        } else {
          default_message_callback();
        };
      };
      read_state = WAITING;
    } else {
      bytes[byte_index] = b;
      byte_index += 1;
    };
  };
}

void BaseComando::default_message_callback() {
  send_message(bytes, n_bytes);
};

void BaseComando::default_error_callback() {
  send_message("error");
};


BaseComando::BaseComando(Stream & communication_stream) {
  stream = &communication_stream;
  message_callback = NULL;
  error_callback = NULL;
  reset();
};

void BaseComando::reset() {
  byte_index = 0;
  n_bytes = 0;
  cs = 0;
  read_state = WAITING;
};

void BaseComando::on_message(callback_function message_handler) {
  message_callback = message_handler;
};

void BaseComando::on_error(callback_function error_handler) {
  error_callback = error_handler;
};

void BaseComando::handle_stream() {
  while (stream->available()) {
    handle_byte(stream->read());
  };
};

void BaseComando::send_message(byte *buffer, byte n) {
  stream->write(n);
  stream->write(buffer, n);
  stream->write(compute_checksum(buffer, n));
};

void BaseComando::send_message(byte *buffer) {
  send_message(buffer, strlen((char *) buffer));
};

void BaseComando::send_message(char *buffer, byte n) {
  send_message((byte *) buffer, n);
};

void BaseComando::send_message(char *buffer) {
  send_message(buffer, strlen(buffer));
};

byte BaseComando::copy_bytes(byte *buffer, byte n) {
  if (n < n_bytes) return 0;
  if (n_bytes == 0) return 0;
  memcpy(buffer, bytes, n_bytes);
  return n_bytes;
};

byte BaseComando::copy_bytes(byte *buffer) {
  return copy_bytes(buffer, n_bytes);
};

byte* BaseComando::get_bytes() {
  return bytes;
};

byte BaseComando::get_n_bytes() {
  return n_bytes;
};

byte BaseComando::get_checksum() {
  return cs;
};


Comando::Comando(Stream & communication_stream): BaseComando(communication_stream) {
  for(byte i=0; i<MAX_CALLBACKS; i++) {
    callbacks[i] = NULL;
  };
};

void Comando::default_message_callback() {
  if (n_bytes == 0) {
    // TODO error
  };
  if (callbacks[bytes[0]] == NULL) {
    // TODO error
  } else {
    (*callbacks[bytes[0]])();
  };
};

void Comando::default_error_callback() {
};

void Comando::attach(byte cmd_id, callback_function callback) {
  callbacks[cmd_id] = callback;
};

Commander::Commander(BaseComando &bcmdo) {
  cmdo = bcmdo;
  for(byte i=0; i<MAX_CALLBACKS; i++) {
    callbacks[i] = NULL;
  };
  error_callback = NULL;
  cmdo->on_message(handle_message);
};

void Commander::error() {
  if (error_callback != NULL) {
    (*error_callback)();
  };
};

void Commander::handle_message(byte *msg_bytes, byte msg_n_bytes) {
  n_bytes = msg_n_bytes;
  bytes = msg_bytes;
  byte_index = 0;
  if (n_bytes == 0) error();
  if (callbacks[bytes[0]] == NULL) {
    error();
  } else {
    (*callbacks[bytes[0]])();
  };
};

void Commander::handle_message(byte *bytes) {
  handle_message(bytes, strlen((char *)bytes));
};

void Commander::handle_message() {
  handle_message(cmdo->get_bytes(), cmdo->get_n_bytes());
};

void Commander::attach(byte cmd_id, callback_function callback) {
  callbacks[cmd_id] = callback;
};
