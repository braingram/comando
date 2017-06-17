
#define S(t) {Serial.print(#t); Serial.print(" "); Serial.println(sizeof(t));}

void setup() {
  Serial.begin(9600);
  S(char)
  S(byte)
  S(int)
  S(unsigned int)
  S(float)
  S(double)
  S(long)
  S(unsigned long)
}

void loop() {
}
