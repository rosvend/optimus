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

void test_stays_expired_until_next_beat() {
  Heartbeat heartbeat;
  heartbeat.beat(100);
  TEST_ASSERT_TRUE(heartbeat.expired(150));
  TEST_ASSERT_TRUE(heartbeat.expired(10));
  heartbeat.beat(100);
  TEST_ASSERT_FALSE(heartbeat.expired(10));
}

void test_new_beat_uses_new_timeout() {
  Heartbeat heartbeat;
  heartbeat.beat(100);
  heartbeat.beat(500);
  TEST_ASSERT_FALSE(heartbeat.expired(400));
  TEST_ASSERT_TRUE(heartbeat.expired(100));
}

void test_time_adds_up_across_small_steps() {
  Heartbeat heartbeat;
  heartbeat.beat(100);
  for (int i = 0; i < 9; i++) TEST_ASSERT_FALSE(heartbeat.expired(10));
  TEST_ASSERT_TRUE(heartbeat.expired(10));
}

int main() {
  UNITY_BEGIN();
  RUN_TEST(test_never_expires_before_first_beat);
  RUN_TEST(test_expires_after_timeout);
  RUN_TEST(test_beat_restarts_the_countdown);
  RUN_TEST(test_stays_expired_until_next_beat);
  RUN_TEST(test_new_beat_uses_new_timeout);
  RUN_TEST(test_time_adds_up_across_small_steps);
  return UNITY_END();
}
