#include "sonar.h"

long echoUsToCm(unsigned long us) {
  if (us == 0) return SONAR_MAX_CM;
  long cm = us / 58;
  return cm > SONAR_MAX_CM ? SONAR_MAX_CM : cm;
}

static long minOf(long a, long b) { return a < b ? a : b; }
static long maxOf(long a, long b) { return a > b ? a : b; }

long SonarFilter::add(long cm) {
  values_[next_] = cm;
  next_ = (next_ + 1) % 3;
  if (count_ < 3) count_++;

  if (count_ == 1) return values_[0];
  if (count_ == 2) return (values_[0] + values_[1]) / 2;

  long a = values_[0], b = values_[1], c = values_[2];
  return maxOf(minOf(a, b), minOf(maxOf(a, b), c));
}
