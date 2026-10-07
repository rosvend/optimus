#include "motor.h"
#include <Arduino.h>

Motor::Motor(int forwardPin, int backwardPin)
    : forwardPin_(forwardPin), backwardPin_(backwardPin) {}

void Motor::drive(int speed) {
  int duty = abs(speed);
  analogWrite(forwardPin_, speed > 0 ? duty : 0);
  analogWrite(backwardPin_, speed < 0 ? duty : 0);
}
