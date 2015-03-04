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

byte BaseComando::get_bytes(byte *buffer, byte n) {
  if (n < n_bytes) return 0;
  if (n_bytes == 0) return 0;
  memcpy(buffer, bytes, n_bytes);
  return n_bytes;
};

byte BaseComando::get_bytes(byte *buffer) {
  return get_bytes(buffer, n_bytes);
};

byte BaseComando::get_nbytes() {
  return n_bytes;
};

byte BaseComando::get_checksum() {
  return cs;
};
