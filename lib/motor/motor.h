#pragma once

// One L298N channel driven by PWM on its two IN pins (EN jumper on).
class Motor {
public:
  Motor(int forwardPin, int backwardPin);
  void drive(int speed);

private:
  int forwardPin_;
  int backwardPin_;
};
