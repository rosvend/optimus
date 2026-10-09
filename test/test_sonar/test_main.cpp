#include <unity.h>
#include "sonar.h"

void test_echo_converts_to_cm() {
  TEST_ASSERT_EQUAL(10, echoUsToCm(580));
}

void test_no_echo_reports_max() {
  TEST_ASSERT_EQUAL(SONAR_MAX_CM, echoUsToCm(0));
}

void test_far_echo_is_clamped_to_max() {
  TEST_ASSERT_EQUAL(SONAR_MAX_CM, echoUsToCm(30000));
}

void test_first_reading_passes_through() {
  SonarFilter filter;
  TEST_ASSERT_EQUAL(42, filter.add(42));
}

void test_two_readings_average() {
  SonarFilter filter;
  filter.add(10);
  TEST_ASSERT_EQUAL(15, filter.add(20));
}

void test_median_drops_spike() {
  SonarFilter filter;
  filter.add(10);
  filter.add(200);
  TEST_ASSERT_EQUAL(12, filter.add(12));
}

void test_median_window_slides() {
  SonarFilter filter;
  filter.add(10);
  filter.add(200);
  filter.add(12);
  // window is now 200, 12, 14
  TEST_ASSERT_EQUAL(14, filter.add(14));
}

int main() {
  UNITY_BEGIN();
  RUN_TEST(test_echo_converts_to_cm);
  RUN_TEST(test_no_echo_reports_max);
  RUN_TEST(test_far_echo_is_clamped_to_max);
  RUN_TEST(test_first_reading_passes_through);
  RUN_TEST(test_two_readings_average);
  RUN_TEST(test_median_drops_spike);
  RUN_TEST(test_median_window_slides);
  return UNITY_END();
}
