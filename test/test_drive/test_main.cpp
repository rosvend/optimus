#include <unity.h>
#include "drive.h"

const int STEP = 50;

void test_forward_speeds_up_both_tracks() {
  Targets t = applyKey({0, 0}, 'w', STEP);
  TEST_ASSERT_EQUAL(50, t.left);
  TEST_ASSERT_EQUAL(50, t.right);
}

void test_backward_slows_both_tracks() {
  Targets t = applyKey({0, 0}, 's', STEP);
  TEST_ASSERT_EQUAL(-50, t.left);
  TEST_ASSERT_EQUAL(-50, t.right);
}

void test_spin_left_drives_tracks_opposite() {
  Targets t = applyKey({0, 0}, 'a', STEP);
  TEST_ASSERT_EQUAL(-50, t.left);
  TEST_ASSERT_EQUAL(50, t.right);
}

void test_spin_right_drives_tracks_opposite() {
  Targets t = applyKey({0, 0}, 'd', STEP);
  TEST_ASSERT_EQUAL(50, t.left);
  TEST_ASSERT_EQUAL(-50, t.right);
}

void test_stop_zeroes_both_tracks() {
  TEST_ASSERT_EQUAL(0, applyKey({100, -100}, 'x', STEP).left);
  TEST_ASSERT_EQUAL(0, applyKey({100, -100}, ' ', STEP).right);
}

void test_unknown_key_keeps_targets() {
  Targets t = applyKey({30, 40}, 'q', STEP);
  TEST_ASSERT_EQUAL(30, t.left);
  TEST_ASSERT_EQUAL(40, t.right);
}

void test_targets_stay_within_full_speed() {
  Targets t = applyKey({240, -240}, 'd', STEP);
  TEST_ASSERT_EQUAL(255, t.left);
  TEST_ASSERT_EQUAL(-255, t.right);
}

int main() {
  UNITY_BEGIN();
  RUN_TEST(test_forward_speeds_up_both_tracks);
  RUN_TEST(test_backward_slows_both_tracks);
  RUN_TEST(test_spin_left_drives_tracks_opposite);
  RUN_TEST(test_spin_right_drives_tracks_opposite);
  RUN_TEST(test_stop_zeroes_both_tracks);
  RUN_TEST(test_unknown_key_keeps_targets);
  RUN_TEST(test_targets_stay_within_full_speed);
  return UNITY_END();
}
