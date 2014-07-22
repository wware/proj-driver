#include <stdlib.h>

// microseconds
#define STEPPER_MOTOR_STEP_TIME   1000

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

/*
 * It would be cool to gradually accelerate the stepper from rest and
 * gradually decelerate to get back to rest, by varying the step time.
 */

void loop() {
    int dir, steps;
    char c;
    if (Serial.available()) {
        buf[bufptr++] = c = (char)Serial.read();
        if (c == '\n') {
            steps = atoi(buf);
            if (steps < 0) {
                digitalWrite(DIRECTION, HIGH);
                steps = -steps;
            } else {
                digitalWrite(DIRECTION, LOW);
            }
            while (steps > 0) {
                delayMicroseconds(STEPPER_MOTOR_STEP_TIME);
                digitalWrite(STEP, HIGH);
                delayMicroseconds(STEPPER_MOTOR_STEP_TIME);
                digitalWrite(STEP, LOW);
                steps--;
            }
            Serial.println("OK");
            bufptr = 0;
            return;
        }
    }
}
