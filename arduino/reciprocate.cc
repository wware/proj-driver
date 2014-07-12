int DIRECTION = 12, STEP = 13;

void setup() {
    pinMode(STEP, OUTPUT);
    pinMode(DIRECTION, OUTPUT);
    digitalWrite(STEP, LOW);
    digitalWrite(DIRECTION, LOW);
}

void briefWait() {
    delayMicroseconds(1000);
}

void run_motor(int dir, int steps) {
    digitalWrite(DIRECTION, dir);
    while (steps > 0) {
        briefWait();
        digitalWrite(STEP, HIGH);
        briefWait();
        digitalWrite(STEP, LOW);
        steps--;
    }
}

void loop() {
	run_motor(0, 1000);
	delayMicroseconds(1000000);
	run_motor(1, 1000);
	delayMicroseconds(1000000);
}
