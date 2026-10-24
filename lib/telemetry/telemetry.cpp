#include "telemetry.h"
#include <stdio.h>

static bool fits(int written, int size) { return written >= 0 && written < size; }

bool formatSonar(char *buf, int size, long cm) {
  return fits(snprintf(buf, size, "s%ld", cm), size);
}

bool formatEnv(char *buf, int size, float tempC, float humPct) {
  return fits(snprintf(buf, size, "e%.1f,%.1f", tempC, humPct), size);
}

// s = sonar, e = environment sensor (temperature/humidity)
bool formatFeatures(char *buf, int size, const char *robotType) {
  return fits(snprintf(buf, size, "f%s:s:e:", robotType), size);
}
