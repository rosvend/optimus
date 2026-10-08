#include <unity.h>
#include "heartbeat.h"

void test_never_expires_before_first_beat() {
  Heartbeat heartbeat;
  TEST_ASSERT_FALSE(heartbeat.expired(100000));
}

void test_expires_after_timeout() {
  Heartbeat heartbeat;
  heartbeat.beat(250);
  TEST_ASSERT_FALSE(heartbeat.expired(200));
  TEST_ASSERT_TRUE(heartbeat.expired(50));
}

void test_beat_restarts_the_countdown() {
  Heartbeat heartbeat;
  heartbeat.beat(250);
  heartbeat.expired(200);
  heartbeat.beat(250);
  TEST_ASSERT_FALSE(heartbeat.expired(200));
}

int main() {
  UNITY_BEGIN();
  RUN_TEST(test_never_expires_before_first_beat);
  RUN_TEST(test_expires_after_timeout);
  RUN_TEST(test_beat_restarts_the_countdown);
  return UNITY_END();
}
