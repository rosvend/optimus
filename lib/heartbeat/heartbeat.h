#pragma once

// Reports when the phone has gone quiet for longer than its announced interval.
class Heartbeat {
public:
  void beat(unsigned long timeoutMs);
  bool expired(unsigned long dtMs);

private:
  bool armed_ = false;
  unsigned long timeoutMs_ = 0;
  unsigned long elapsedMs_ = 0;
};
