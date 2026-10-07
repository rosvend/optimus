#include "ramp.h"
#include <math.h>

const int MAX_SPEED = 255;

SpeedRamp::SpeedRamp(float ratePerSecond, unsigned long reversePauseMs)
    : rate_(ratePerSecond), pauseMs_(reversePauseMs) {}

void SpeedRamp::setTarget(int target) {
  if (target > MAX_SPEED) target = MAX_SPEED;
  if (target < -MAX_SPEED) target = -MAX_SPEED;
  target_ = target;
}

int SpeedRamp::update(unsigned long dtMs) {
  if (current_ == 0 && pauseLeft_ > 0) {
    pauseLeft_ = dtMs >= pauseLeft_ ? 0 : pauseLeft_ - dtMs;
    return 0;
  }

  bool reversing = current_ * target_ < 0;
  float goal = reversing ? 0 : target_;
  float step = rate_ * dtMs / 1000.0f;
  bool wasMoving = current_ != 0;

  if (fabsf(goal - current_) <= step) current_ = goal;
  else current_ += goal > current_ ? step : -step;

  if (wasMoving && current_ == 0) pauseLeft_ = pauseMs_;
  return (int)lroundf(current_);
}
