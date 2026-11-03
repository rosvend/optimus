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

void test_echo_shorter_than_one_cm_is_zero() {
  TEST_ASSERT_EQUAL(0, echoUsToCm(57));
  TEST_ASSERT_EQUAL(1, echoUsToCm(58));
}

void test_echo_at_max_range_is_not_clamped() {
  TEST_ASSERT_EQUAL(SONAR_MAX_CM, echoUsToCm(SONAR_MAX_CM * 58));
  TEST_ASSERT_EQUAL(SONAR_MAX_CM - 1, echoUsToCm(SONAR_MAX_CM * 58 - 1));
}

void test_median_of_unsorted_window() {
  SonarFilter filter;
  filter.add(30);
  filter.add(10);
  TEST_ASSERT_EQUAL(20, filter.add(20));
}

void test_steady_readings_pass_through() {
  SonarFilter filter;
  for (int i = 0; i < 5; i++) TEST_ASSERT_EQUAL(75, filter.add(75));
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
  RUN_TEST(test_echo_shorter_than_one_cm_is_zero);
  RUN_TEST(test_echo_at_max_range_is_not_clamped);
  RUN_TEST(test_median_of_unsorted_window);
  RUN_TEST(test_steady_readings_pass_through);
  return UNITY_END();
}
