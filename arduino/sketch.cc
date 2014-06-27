char inChar;
int dir, steps;
int communicating = 0;

int DIRECTION = 12, STEP = 13;

void setup() {
  Serial.begin(9600);
  inChar = '\0';
  digitalWrite(STEP, LOW);
}

void briefWait() {
  delayMicroseconds(1 * 1000);
}

void loop() {
  if (!communicating) {
    Serial.println("A");
    delay(500);
  }
  else if (inChar != '\0') {
    digitalWrite(DIRECTION, dir);
    while (steps > 0) {
      briefWait();
      digitalWrite(STEP, HIGH);
      briefWait();
      digitalWrite(STEP, LOW);
      steps--;
    }
    Serial.print(inChar);
    inChar = '\0';
  }
}

void serialEvent() {
  if (!communicating) {
    Serial.println("OK");
    communicating = 1;
    return;
  }
  while (Serial.available()) {
    inChar = (char)Serial.read();
    Serial.print(inChar);
    switch (inChar) {
      case 'j':
        dir = LOW;
        steps = 90;
        break;
      case 'k':
        dir = HIGH;
        steps = 90;
        break;
      case 'J':
        dir = LOW;
        steps = 900;
        break;
      case 'K':
        dir = HIGH;
        steps = 900;
        break;
      case 'U':
        dir = LOW;
        steps = 9000;
        break;
      case 'I':
        dir = HIGH;
        steps = 9000;
        break;
      default:
        steps = 0;
        break;
    }
  }
}