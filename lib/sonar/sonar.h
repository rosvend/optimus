#pragma once

// Distance reported when there is no echo or the obstacle is out of range.
const long SONAR_MAX_CM = 300;

// HC-SR04 echo pulse width (us) to cm; 0 means the echo timed out.
long echoUsToCm(unsigned long us);

// Median of the last 3 readings, to drop the HC-SR04's occasional spikes.
class SonarFilter {
public:
  long add(long cm);

private:
  long values_[3] = {0, 0, 0};
  int count_ = 0;
  int next_ = 0;
};
