
float numbers[3] = {0.0, 0.0, 0.0};

void setup(){
  Serial.begin(115200);
  while (Serial.available()) Serial.read();
}

void loop() {
  if (Serial.available()) {
    numbers[0] = Serial.parseFloat();
    numbers[1] = Serial.parseFloat();
    numbers[2] = Serial.parseFloat();
    Serial.print(numbers[0], DEC);
    Serial.print(',');
    Serial.print(numbers[1], DEC);
    Serial.print(',');
    Serial.print(numbers[2], DEC);
    Serial.print('\n');
  }
}
