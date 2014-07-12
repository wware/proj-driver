#include <stdlib.h>

char buf[10];
int bufptr;

int DIRECTION = 12, STEP = 13;

void setup() {
    Serial.begin(9600);
    pinMode(STEP, OUTPUT);
    pinMode(DIRECTION, OUTPUT);
    digitalWrite(STEP, LOW);
    digitalWrite(DIRECTION, LOW);
    bufptr = 0;
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
    int dir, steps;
    char c;
    while (Serial.available()) {
        buf[bufptr++] = c = (char)Serial.read();
        if (c == '\n') {
            steps = atoi(buf);
            if (steps < 0) {
                dir = 1;
                steps = -steps;
            } else {
                dir = 0;
            }
            run_motor(dir, steps);
            Serial.println("OK");
            bufptr = 0;
            return;
        }
    }
}
