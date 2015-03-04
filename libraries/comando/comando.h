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

byte compute_checksum(byte *bytes, byte n);

enum {
  READING,
  WAITING,
};

class BaseComando {
  private:
    byte byte_index;
    byte n_bytes;
    byte bytes[MAX_MSG_LENGTH];
    byte cs;
    byte read_state;
    Stream *stream;
    callback_function message_callback;
    callback_function error_callback;

    void handle_byte(byte b);
    void default_message_callback();
    void default_error_callback();

  public:
    BaseComando(Stream & communication_stream);

    void reset();
    void on_message(callback_function message_handler);
    void on_error(callback_function error_handler);
    void handle_stream();

    void send_message(byte *buffer, byte n);
    void send_message(byte *buffer);
    void send_message(char *buffer, byte n);
    void send_message(char *buffer);

    byte get_bytes(byte *buffer, byte n);
    byte get_bytes(byte *buffer);
    byte get_nbytes();
    byte get_checksum();
};
#endif
