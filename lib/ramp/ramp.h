#pragma once

// Slew-rate limited speed (-255..255) that stops and pauses before reversing.
class SpeedRamp {
public:
  SpeedRamp(float ratePerSecond, unsigned long reversePauseMs);
  void setTarget(int target);
  int target() const { return target_; }
  int update(unsigned long dtMs);

private:
  float rate_;
  unsigned long pauseMs_;
  unsigned long pauseLeft_ = 0;
  float current_ = 0;
  int target_ = 0;
};
