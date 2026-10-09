#include <unity.h>
#include "telemetry.h"

void test_sonar_line() {
  char buf[16];
  TEST_ASSERT_TRUE(formatSonar(buf, sizeof(buf), 42));
  TEST_ASSERT_EQUAL_STRING("s42", buf);
}

void test_env_line() {
  char buf[24];
  TEST_ASSERT_TRUE(formatEnv(buf, sizeof(buf), 23.4f, 61.2f));
  TEST_ASSERT_EQUAL_STRING("e23.4,61.2", buf);
}

void test_env_negative_temperature() {
  char buf[24];
  TEST_ASSERT_TRUE(formatEnv(buf, sizeof(buf), -3.5f, 80.0f));
  TEST_ASSERT_EQUAL_STRING("e-3.5,80.0", buf);
}

void test_env_rounds_to_one_decimal() {
  char buf[24];
  TEST_ASSERT_TRUE(formatEnv(buf, sizeof(buf), 23.46f, 61.24f));
  TEST_ASSERT_EQUAL_STRING("e23.5,61.2", buf);
}

void test_features_line() {
  char buf[32];
  TEST_ASSERT_TRUE(formatFeatures(buf, sizeof(buf), "OPTIMUS"));
  TEST_ASSERT_EQUAL_STRING("fOPTIMUS:s:e:", buf);
}

void test_small_buffer_is_rejected_and_terminated() {
  char buf[3];
  TEST_ASSERT_FALSE(formatSonar(buf, sizeof(buf), 300));
  TEST_ASSERT_EQUAL('\0', buf[2]);
}

int main() {
  UNITY_BEGIN();
  RUN_TEST(test_sonar_line);
  RUN_TEST(test_env_line);
  RUN_TEST(test_env_negative_temperature);
  RUN_TEST(test_env_rounds_to_one_decimal);
  RUN_TEST(test_features_line);
  RUN_TEST(test_small_buffer_is_rejected_and_terminated);
  return UNITY_END();
}
