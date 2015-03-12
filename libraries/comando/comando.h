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
#define MAX_PROTOCOLS 10

byte compute_checksum(byte *bytes, byte n);

enum {
  READING,
  WAITING,
};

class Comando;

class Protocol {
  protected:
    Comando *cmdo;
    byte index;
    byte buffer[MAX_MSG_LENGTH];  // for sending
    byte buffern;
  public:
    Protocol(Comando & bcmdo);
    virtual void start_message();
    virtual void build_message(byte *bytes, byte n_bytes);
    virtual void finish_message();
    virtual void send_message(byte *bytes, byte n_bytes);
    virtual void receive_message(byte *bytes, byte n_bytes);
    void set_index(byte i);
    byte get_index();
};

class TextProtocol: public Protocol {
};

class EchoProtocol: public Protocol {
  public:
    EchoProtocol(Comando & bcmdo);
    void receive_message(byte *bytes, byte n_bytes);
};

class CommandProtocol: public Protocol {
  protected:
    byte arg_index;
    byte arg_buffer[MAX_MSG_LENGTH];  // for receiving
    byte arg_buffern;
    callback_function callbacks[MAX_CALLBACKS];
  public:
    CommandProtocol(Comando & bcmdo);
    void receive_message(byte *bytes, byte n_bytes);
    void register_callback(byte index, callback_function callback);
    void start_command(byte cid);
    template <typename T> void add_arg(T arg) {
      build_message((byte *) &arg, sizeof(T));
    };
    void finish_command();
    void send_command(byte cid);
    template <typename T> T get_arg() {
      T value;
      memcpy((byte *)&value, arg_buffer+arg_index, sizeof(T));
      arg_index += sizeof(T);
      return value;
    };
};

class Comando {
  protected:
    byte byte_index;
    byte n_bytes;
    byte bytes[MAX_MSG_LENGTH];
    byte cs;
    byte read_state;
    Stream *stream;
    callback_function message_callback;
    Protocol *protocols[MAX_PROTOCOLS];

    void receive_byte(byte b);
    virtual void default_message_callback();

  public:
    Comando(Stream & communication_stream);

    void register_protocol(byte index, Protocol & protocol);

    void reset();
    void register_message_callback(callback_function message_handler);
    void unregister_message_callback();

    void send_message(byte *buffer, byte n);
    void send_message(byte *buffer);
    void send_message(char *buffer, byte n);
    void send_message(char *buffer);

    byte copy_bytes(byte *buffer, byte n);
    byte copy_bytes(byte *buffer);
    byte* get_bytes();
    byte get_n_bytes();
    byte get_checksum();

    void handle_stream();
};

#endif
