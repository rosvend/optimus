#include "motor.h"
#include <Arduino.h>

// A reversed motor just swaps its pins, same as swapping the wires on the L298N
Motor::Motor(int forwardPin, int backwardPin, bool reversed)
    : forwardPin_(reversed ? backwardPin : forwardPin),
      backwardPin_(reversed ? forwardPin : backwardPin) {}

void Motor::drive(int speed) {
  int duty = abs(speed);
  analogWrite(forwardPin_, speed > 0 ? duty : 0);
  analogWrite(backwardPin_, speed < 0 ? duty : 0);
}
