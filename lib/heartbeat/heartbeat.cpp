#include "heartbeat.h"

void Heartbeat::beat(unsigned long timeoutMs) {
  armed_ = true;
  timeoutMs_ = timeoutMs;
  elapsedMs_ = 0;
}

bool Heartbeat::expired(unsigned long dtMs) {
  if (!armed_) return false;
  elapsedMs_ += dtMs;
  return elapsedMs_ >= timeoutMs_;
}
