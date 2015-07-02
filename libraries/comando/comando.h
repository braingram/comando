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


class Comando;
class Protocol;
class CommandProtocol;

extern "C" {
  typedef void (*callback_function) (void);
  typedef void (*command_callback) (CommandProtocol *protocol);
}

#define MAX_MSG_LENGTH 255
#define MAX_CALLBACKS 50
#define MAX_PROTOCOLS 10
#define MAX_STRING_ARG_LENGTH 16

#define LOG_DEBUG 10
#define LOG_INFO 20
#define LOG_WARN 30
#define LOG_WARNING 30
#define LOG_ERROR 40
#define LOG_CRITICAL 50
#define LOG_FATAL 50

byte compute_checksum(byte *bytes, byte n);

enum {
  READING,
  WAITING,
};

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
  public:
    TextProtocol(Comando & bcmdo);
};

class EchoProtocol: public Protocol {
  public:
    EchoProtocol(Comando & bcmdo);
    void receive_message(byte *bytes, byte n_bytes);
};

class LogProtocol: public Protocol {
  public:
    LogProtocol(Comando & bcmdo);
    void log(byte level, char *msg);
    void debug(char *msg);
    void info(char *msg);
    void warn(char *msg);
    void warning(char *msg);
    void error(char *msg);
    void critical(char *msg);
    void fatal(char *msg);
};


class CommandProtocol: public Protocol {
  protected:
    byte arg_index;
    byte arg_buffer[MAX_MSG_LENGTH];  // for receiving
    byte arg_buffern;
    char string_arg_buffer[MAX_STRING_ARG_LENGTH];
    command_callback callbacks[MAX_CALLBACKS];
  public:
    CommandProtocol(Comando & bcmdo);
    void receive_message(byte *bytes, byte n_bytes);
    void register_callback(byte index, command_callback callback);
    void start_command(byte cid);
    template <typename T> void add_arg(T arg) {
      build_message((byte *) &arg, sizeof(T));
    };

    void add_string_arg(String s) {
      // prepend length
      byte n = (byte) s.length();
      build_message(&n, 1);
      build_message((byte *) s.c_str(), s.length());
    };

    void finish_command();
    void send_command(byte cid);
    bool has_arg();
    template <typename T> T get_arg() {
      if (!has_arg()) return NULL;
      T value;
      memcpy((byte *)&value, arg_buffer+arg_index, sizeof(T));
      arg_index += sizeof(T);
      return value;
    };

    String get_string_arg() {
      if (!has_arg()) return NULL;
      // read size of arg_buffer string [first byte]
      byte n = *(arg_buffer+arg_index);
      arg_index += 1;
      if (n == '\x00') {  // if a 0 length string, just return s
          return String("");
      };
      // copy arg_buffer into string
      memcpy(string_arg_buffer, arg_buffer+arg_index, n);
      String s = String(string_arg_buffer);
      arg_index += n;
      return s;
    };
};

class Comando {
  protected:
    byte byte_index;
    byte n_bytes;
    byte bytes[MAX_MSG_LENGTH];
    byte cs;
    byte read_state;
    int error_protocol;
    Stream *stream;
    callback_function message_callback;
    Protocol *protocols[MAX_PROTOCOLS];

    void receive_byte(byte b);
    virtual void default_message_callback();

  public:
    Comando(Stream & communication_stream);

    void register_protocol(byte index, Protocol & protocol);
    void set_error_protocol(int pid);

    void reset();
    void register_message_callback(callback_function message_handler);
    void unregister_message_callback();

    void send_message(byte *buffer, byte n);
    void send_message(byte *buffer);
    void send_message(char *buffer, byte n);
    void send_message(char *buffer);

    void send_error(char *buffer, byte n);
    void send_error(char *buffer);

    byte copy_bytes(byte *buffer, byte n);
    byte copy_bytes(byte *buffer);
    byte* get_bytes();
    byte get_n_bytes();
    byte get_checksum();

    void handle_stream();
};

#endif
