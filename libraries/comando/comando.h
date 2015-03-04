/* 
 * Comando
 *
 * written by Brett Graham, March 2015
 */

#ifndef COMANDO
#define COMANDO

#include <inttypes.h>
#if ARDUINO >= 100
#include <Arduino.h> 
#else
#include <WProgram.h> 
#endif

extern "C" {
  typedef void (*callback_function) (void);
}

#define MAX_MSG_LENGTH 255

byte compute_checksum(byte *bytes, byte n) {
    byte cs = 0;
    for (byte i=0; i<n; i++) cs += bytes[i];
    return cs;
};

enum {
  READING,
  WAITING,
};

class Comando {
  private:
    byte byte_index;
    byte n_bytes;
    byte bytes[MAX_MSG_LENGTH];
    byte cs;
    byte read_state;
    Stream *stream;
    callback_function message_callback;
    callback_function error_callback;

    void handle_byte(byte b) {
      if (read_state == WAITING) {
        // this is n
        n_bytes = b;
        byte_index = 0;
        read_state = READING;
      } else {  // READING
        if (byte_index == n_bytes) {  // b = checksum
          cs = b;
          if (cs != compute_checksum(bytes, n_bytes)) {
            if (error_callback != NULL)
              (*error_callback)();
          } else {
            if (message_callback != NULL)
              (*message_callback)();
          };
          read_state = WAITING;
        } else {
          bytes[byte_index] = b;
          byte_index += 1;
        };
      };
    }

  public:
    Comando(Stream & communication_stream) {
      stream = &communication_stream;
      message_callback = NULL;
      error_callback = NULL;
      reset();
    };

    void reset() {
      byte_index = 0;
      n_bytes = 0;
      cs = 0;
      read_state = WAITING;
    };

    void on_message(callback_function message_handler) {
      message_callback = message_handler;
    };

    void on_error(callback_function error_handler) {
      error_callback = error_handler;
    };

    void handle_stream() {
      while (stream->available()) {
        handle_byte(stream->read());
      };
    };

    void send_message(byte *buffer, byte n) {
      stream->write(n);
      stream->write(buffer, n);
      stream->write(compute_checksum(buffer, n));
    };

    void send_message(byte *buffer) {
      send_message(buffer, strlen((char *) buffer));
    };

    void send_message(char *buffer, byte n) {
      send_message((byte *) buffer, n);
    };

    void send_message(char *buffer) {
      send_message(buffer, strlen(buffer));
    };

    byte get_bytes(byte *buffer, byte n) {
      if (n < n_bytes) return 0;
      if (n_bytes == 0) return 0;
      memcpy(buffer, bytes, n_bytes);
      return n_bytes;
    };

    byte get_bytes(byte *buffer) {
      return get_bytes(buffer, n_bytes);
    };

    byte get_nbytes() {
      return n_bytes;
    };

    byte get_checksum() {
      return cs;
    };
};
#endif
