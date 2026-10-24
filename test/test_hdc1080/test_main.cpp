#include <unity.h>
#include "hdc1080.h"

void test_temperature_zero_raw_is_minus_40() {
  TEST_ASSERT_FLOAT_WITHIN(0.01f, -40.0f, hdcTemperatureC(0x0000));
}

void test_temperature_mid_raw() {
  TEST_ASSERT_FLOAT_WITHIN(0.01f, 21.875f, hdcTemperatureC(0x6000));
}

void test_humidity_half_raw_is_50() {
  TEST_ASSERT_FLOAT_WITHIN(0.01f, 50.0f, hdcHumidityPct(0x8000));
}

void test_humidity_full_raw_is_just_under_100() {
  TEST_ASSERT_FLOAT_WITHIN(0.01f, 99.998f, hdcHumidityPct(0xFFFF));
}

int main() {
  UNITY_BEGIN();
  RUN_TEST(test_temperature_zero_raw_is_minus_40);
  RUN_TEST(test_temperature_mid_raw);
  RUN_TEST(test_humidity_half_raw_is_50);
  RUN_TEST(test_humidity_full_raw_is_just_under_100);
  return UNITY_END();
}
