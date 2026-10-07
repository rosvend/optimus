#include <unity.h>
#include "ramp.h"

// 255 units/s, 300 ms pause at zero before reversing
SpeedRamp makeRamp() { return SpeedRamp(255.0f, 300); }

void runFor(SpeedRamp &ramp, int ms) {
  for (int i = 0; i < ms / 10; i++) ramp.update(10);
}

void test_starts_stopped() {
  SpeedRamp ramp = makeRamp();
  TEST_ASSERT_EQUAL(0, ramp.update(10));
}

void test_accelerates_gradually() {
  SpeedRamp ramp = makeRamp();
  ramp.setTarget(255);
  TEST_ASSERT_INT_WITHIN(1, 26, ramp.update(100));
}

void test_reaches_target_without_overshoot() {
  SpeedRamp ramp = makeRamp();
  ramp.setTarget(100);
  runFor(ramp, 2000);
  TEST_ASSERT_EQUAL(100, ramp.update(10));
}

void test_clamps_target() {
  SpeedRamp ramp = makeRamp();
  ramp.setTarget(999);
  runFor(ramp, 3000);
  TEST_ASSERT_EQUAL(255, ramp.update(10));
}

void test_stop_decelerates_gradually() {
  SpeedRamp ramp = makeRamp();
  ramp.setTarget(255);
  runFor(ramp, 2000);
  ramp.setTarget(0);
  TEST_ASSERT_INT_WITHIN(1, 229, ramp.update(100));
}

void test_reversal_passes_through_zero_and_pauses() {
  SpeedRamp ramp = makeRamp();
  ramp.setTarget(255);
  runFor(ramp, 2000);
  ramp.setTarget(-255);

  int previous = 255;
  int msAtZero = 0;
  for (int i = 0; i < 300; i++) {
    int speed = ramp.update(10);
    TEST_ASSERT_TRUE(speed <= previous || previous <= 0);
    TEST_ASSERT_FALSE(previous > 0 && speed < 0);
    if (speed == 0) msAtZero += 10;
    previous = speed;
  }
  TEST_ASSERT_TRUE(msAtZero >= 300);
  TEST_ASSERT_EQUAL(-255, previous);
}

int main() {
  UNITY_BEGIN();
  RUN_TEST(test_starts_stopped);
  RUN_TEST(test_accelerates_gradually);
  RUN_TEST(test_reaches_target_without_overshoot);
  RUN_TEST(test_clamps_target);
  RUN_TEST(test_stop_decelerates_gradually);
  RUN_TEST(test_reversal_passes_through_zero_and_pauses);
  return UNITY_END();
}
