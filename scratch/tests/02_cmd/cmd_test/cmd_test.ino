
#define MAX_MSG_LENGTH 255

byte i = 0;
byte rn = 0;
byte n = 0;
byte bs[MAX_MSG_LENGTH];
byte ccs = 0;
byte cs = 0;

int t = 0;
int led = 13;
boolean led_enabled = true;
unsigned long led_delay = 500;
boolean led_on = false;

float f = 0.;

void setup() {
  pinMode(led, OUTPUT);
  led_enabled = true;
  digitalWrite(led, HIGH);
  led_on = true;
  
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

void write_message(byte n) {
  ccs = 0;
  for (i=0; i<n; i++) {
    ccs += bs[i];
  }
  Serial.write(n);
  Serial.write(bs, n);
  Serial.write(ccs);
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
      rn = Serial.readBytes((char *)bs, n);
      if (rn != n) {
        Serial.print("Invalid read: ");
        Serial.print(rn);
        Serial.print(" != ");
        Serial.println(n);
      }
      for (i=0; i<n; i++) {
        //bs[i] = wait_and_read();
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
    if (n == 0) {
      Serial.println("Invalid message missing payload");
    };
    switch(bs[0]) {
      case '\x00':
        // toggle blink (no args)
        led_enabled = !led_enabled;
        break;
      case '\x01':
        if (n != 2) {
          Serial.println("Invalid message missing arg");
        };
        // enable/disable blink (boolean)
        led_enabled = (boolean) bs[1];
        break;
      case '\x02':
        // set blink time (int)
        if (n != 5) {
          Serial.println("Invalid message missing arg");
        };
        memcpy(&led_delay, bs + 1, sizeof(unsigned long));
        //led_delay = (unsigned long) (bs + 1);
        Serial.println(led_delay);
        break;
      case '\x03':
        // echo float (float)
        memcpy(&f, bs + 1, sizeof(float));
        Serial.println(f,12);
        break;
      default:
        Serial.print("Invalid command: ");
        Serial.println(bs[0]);
    };
    // send back the message
  };
  if (led_enabled) {
    if (led_on) {
      digitalWrite(led, LOW);
      led_on = false;
    } else {
      digitalWrite(led, HIGH);
      led_on = true;
    }
    delay(led_delay);
  } else {
    digitalWrite(led, LOW);
    led_on = false;
  };
}
