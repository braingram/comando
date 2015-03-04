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
#define MAX_CALLBACKS 50

byte compute_checksum(byte *bytes, byte n);

enum {
  READING,
  WAITING,
};

class BaseComando {
  protected:
    byte byte_index;
    byte n_bytes;
    byte bytes[MAX_MSG_LENGTH];
    byte cs;
    byte read_state;
    Stream *stream;
    callback_function message_callback;
    callback_function error_callback;

    void handle_byte(byte b);
    virtual void default_message_callback();
    virtual void default_error_callback();

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

    byte copy_bytes(byte *buffer, byte n);
    byte copy_bytes(byte *buffer);
    byte* get_bytes();
    byte get_n_bytes();
    byte get_checksum();
};


class Comando: public BaseComando {
  protected:
    void default_message_callback();
    void default_error_callback();
    callback_function callbacks[MAX_CALLBACKS];
    // TODO unknown callback?
  public:
    Comando(Stream & communication_stream);

    void attach(byte cmd_id, callback_function callback);
    template <class T> T read_arg() {
      byte n = sizeof(T);
      T result;
      if (byte_index + n < n_bytes) {
        memcpy(&result, bytes + byte_index, n);
        byte_index += n;
      } else {
        // TODO error, attempt to read too many args
      };
      return result;
    };
    // TODO functions to pack args
};

class Commander {
  protected:
    BaseComando *cmdo;
    byte byte_index;
    byte *bytes;
    byte n_bytes;
    callback_function error_callback;
    callback_function callbacks[MAX_CALLBACKS];
  public:
    Commander(BaseComando &bcmdo);

    void error();
    void handle_message(byte *bytes, byte n_bytes);
    void handle_message(byte *bytes);
    void attach(byte cmd_id, callback_function callback);

    template <class T> T read_arg() {
      byte n = sizeof(T);
      T result;
      if (byte_index + n < n_bytes) {
        memcpy(&result, bytes + byte_index, n);
        byte_index += n;
      } else {
        error();
      };
      return result;
    };
    // TODO functions to pack args
};

#endif
