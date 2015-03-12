#include <comando.h>

byte compute_checksum(byte *bytes, byte n) {
  byte cs = 0;
  for (byte i=0; i<n; i++) cs += bytes[i];
  return cs;
};


Protocol::Protocol(Comando & bcmdo) {
  cmdo = &bcmdo;
};

void Protocol::set_index(byte i) {
  index = i;
};

byte Protocol::get_index() {
  return index;
};


void Protocol::start_message() {
  buffer[0] = index;
  buffern = 1;
};

void Protocol::build_message(byte *bytes, byte n_bytes) {
  // copy bytes in buffer[buffern:buffern+n_bytes]
  memcpy(buffer+buffern, bytes, n_bytes);
  buffern += n_bytes;
};

void Protocol::finish_message() {
  cmdo->send_message(buffer, buffern);
};

void Protocol::send_message(byte *bytes, byte n_bytes) {
  start_message();
  build_message(bytes, n_bytes);
  finish_message();
  //cmdo->send_message(bytes, n_bytes);
};

void Protocol::receive_message(byte *bytes, byte n_bytes) {
};

// =============== EchoProtocol ============
EchoProtocol::EchoProtocol(Comando & bcmdo): Protocol(bcmdo) {};

void EchoProtocol::receive_message(byte *bytes, byte n_bytes) {
  send_message(bytes, n_bytes);
};

// =============== CommandProtocol ============
CommandProtocol::CommandProtocol(Comando & bcmdo): Protocol(bcmdo) {
  for(byte i=0; i<MAX_CALLBACKS; i++) {
    callbacks[i] = NULL;
  };
};

void CommandProtocol::receive_message(byte *bytes, byte n_bytes) {
  if (n_bytes == 0) {
    // TODO error
  };
  if (callbacks[bytes[0]] == NULL) {
    // TODO error
  } else {
    arg_index = 0;
    if (n_bytes > 1) {
      arg_buffern = n_bytes - 1;
      memcpy(arg_buffer, bytes+1, arg_buffern);
    } else {
      arg_buffern = 0;
    };
    (*callbacks[bytes[0]])();
  };
};

void CommandProtocol::register_callback(byte index, callback_function callback) {
  callbacks[index] = callback;
};

void CommandProtocol::start_command(byte cid) {
  start_message();
  build_message(&cid, 1);
};

void CommandProtocol::finish_command() {
  finish_message();
};

void CommandProtocol::send_command(byte cid) {
  start_command(cid);
  finish_command();
};

// ================= Comando ==========
void Comando::receive_byte(byte b) {
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
        // TODO error
      } else {
        if (message_callback != NULL) {
          // TODO should the return value determine if default is called?
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

void Comando::default_message_callback() {
  if (n_bytes < 1) {
    // TODO error
  } else {
    if (protocols[bytes[0]] == NULL) {
      // TODO error
    } else {
      Protocol *p = protocols[bytes[0]];
      p->receive_message(bytes+1, n_bytes-1);
    };
  };
};


Comando::Comando(Stream & communication_stream) {
  stream = &communication_stream;
  message_callback = NULL;
  for (byte i=0; i<MAX_PROTOCOLS; i++) {
    protocols[i] = NULL;
  };
  reset();
};

void Comando::reset() {
  byte_index = 0;
  n_bytes = 0;
  cs = 0;
  read_state = WAITING;
};

void Comando::register_message_callback(callback_function message_handler) {
  message_callback = message_handler;
};

void Comando::unregister_message_callback() {
  message_callback = NULL;
};

void Comando::handle_stream() {
  while (stream->available()) {
    receive_byte(stream->read());
  };
};

void Comando::send_message(byte *buffer, byte n) {
  stream->write(n);
  stream->write(buffer, n);
  stream->write(compute_checksum(buffer, n));
};

void Comando::send_message(byte *buffer) {
  send_message(buffer, strlen((char *) buffer));
};

void Comando::send_message(char *buffer, byte n) {
  send_message((byte *) buffer, n);
};

void Comando::send_message(char *buffer) {
  send_message(buffer, strlen(buffer));
};

byte Comando::copy_bytes(byte *buffer, byte n) {
  if (n < n_bytes) return 0;
  if (n_bytes == 0) return 0;
  memcpy(buffer, bytes, n_bytes);
  return n_bytes;
};

byte Comando::copy_bytes(byte *buffer) {
  return copy_bytes(buffer, n_bytes);
};

byte* Comando::get_bytes() {
  return bytes;
};

byte Comando::get_n_bytes() {
  return n_bytes;
};

byte Comando::get_checksum() {
  return cs;
};

void Comando::register_protocol(byte index, Protocol & protocol) {
  if (index < MAX_PROTOCOLS) {
    protocols[index] = &protocol;
    protocol.set_index(index);
  } else {
    // TODO error
  };
};
