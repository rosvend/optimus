#include <stdlib.h>
#include <unity.h>
#include "config/ramp_config.h"
#include "ramp.h"

const unsigned long DT_MS = 10;

// Whatever the phone sends, the output must slew gradually and rest at zero before reversing
void test_random_commands_never_break_motor_limits() {
  srand(42);
  SpeedRamp ramp(ACCEL_PER_SECOND, REVERSE_PAUSE_MS);

  int previous = 0;
  int lastDirection = 0;
  unsigned long zeroMs = 0;
  int stepsUntilNewCommand = 0;
  int maxStep = (int)(ACCEL_PER_SECOND * DT_MS / 1000.0f) + 1;

  for (int i = 0; i < 500000; i++) {
    if (stepsUntilNewCommand-- <= 0) {
      int roll = rand() % 4;
      int target = roll == 0 ? 255 : roll == 1 ? -255 : (rand() % 511) - 255;
      ramp.setTarget(target);
      stepsUntilNewCommand = 1 + rand() % 40;
    }

    int output = ramp.update(DT_MS);

    TEST_ASSERT_TRUE(abs(output - previous) <= maxStep);
    TEST_ASSERT_FALSE(previous > 0 && output < 0);
    TEST_ASSERT_FALSE(previous < 0 && output > 0);

    if (output == 0) {
      zeroMs += DT_MS;
    } else {
      int direction = output > 0 ? 1 : -1;
      if (lastDirection != 0 && direction != lastDirection) {
        TEST_ASSERT_TRUE(zeroMs >= REVERSE_PAUSE_MS);
      }
      lastDirection = direction;
      zeroMs = 0;
    }
    previous = output;
  }
}

int main() {
  UNITY_BEGIN();
  RUN_TEST(test_random_commands_never_break_motor_limits);
  return UNITY_END();
}
