
#define MAX_MSG_LENGTH 255

byte i = 0;
byte n = 0;
byte bs[MAX_MSG_LENGTH];
byte ccs = 0;
byte cs = 0;

void setup() {
  Serial.begin(9600);
  
  // clear byte buffer
  for (i=0; i<MAX_MSG_LENGTH; i++) {
    bs[i] = '\x00';
  };
}

byte wait_and_read() {
  while (Serial.available() < 1) {};
  return Serial.read();
}

void loop() {
  if (Serial.available() > 0) {
    // read message length
    n = wait_and_read();
    // read bytes
    if (n == 0) {
      ccs = 0;
    } else {  // msg contains bytes
      ccs = 0;
      for (i=0; i<n; i++) {
        bs[i] = wait_and_read();
        ccs += bs[i];
      };
    };
    // read checksum
    cs = wait_and_read();
    if (cs != ccs) {
      Serial.println("Error Invalid Checksum");
      Serial.print(ccs);
      Serial.print(" != ");
      Serial.println(cs);
    };
    // send back the message
    Serial.write(n);
    Serial.write(bs, n);
    Serial.write(ccs);
  };
}
