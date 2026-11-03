#include "config/ramp_config.h"
#include "config/sensors_config.h"
#include "hdc1080.h"
#include "heartbeat.h"
#include "openbot_parser.h"
#include "ramp.h"
#include "sonar.h"
#include "telemetry.h"
#include <unity.h>

// Mirrors how src/openbot/main.cpp wires the parser, heartbeat and ramps, without the Arduino core
struct Robot {
  OpenBotParser parser;
  Heartbeat heartbeat;
  SpeedRamp left{ACCEL_PER_SECOND, REVERSE_PAUSE_MS};
  SpeedRamp right{ACCEL_PER_SECOND, REVERSE_PAUSE_MS};
  int leftOut = 0;
  int rightOut = 0;

  void receive(const char *text) {
    for (const char *c = text; *c; c++) {
      Message m = parser.feed(*c);
      if (m.type == MessageType::Control) {
        left.setTarget(m.left);
        right.setTarget(m.right);
      } else if (m.type == MessageType::Heartbeat) {
        heartbeat.beat(m.intervalMs);
      }
    }
  }

  void tick(unsigned long dtMs) {
    if (heartbeat.expired(dtMs)) {
      left.setTarget(0);
      right.setTarget(0);
    }
    leftOut = left.update(dtMs);
    rightOut = right.update(dtMs);
  }

  void run(unsigned long ms) {
    for (unsigned long t = 0; t < ms; t += 10) tick(10);
  }
};

void test_control_command_drives_both_tracks_forward() {
  Robot robot;
  robot.receive("c200,200\n");
  robot.run(2000);
  TEST_ASSERT_EQUAL(200, robot.leftOut);
  TEST_ASSERT_EQUAL(200, robot.rightOut);
}

void test_spin_command_drives_tracks_in_opposite_directions() {
  Robot robot;
  robot.receive("c-120,120\n");
  robot.run(2000);
  TEST_ASSERT_EQUAL(-120, robot.leftOut);
  TEST_ASSERT_EQUAL(120, robot.rightOut);
}

void test_command_split_across_reads_is_applied_once_complete() {
  Robot robot;
  robot.receive("c100,");
  robot.run(500);
  TEST_ASSERT_EQUAL(0, robot.leftOut);
  robot.receive("100\n");
  robot.run(2000);
  TEST_ASSERT_EQUAL(100, robot.leftOut);
}

void test_silent_phone_stops_the_robot() {
  Robot robot;
  robot.receive("h250\nc150,150\n");
  robot.run(3000);
  TEST_ASSERT_EQUAL(0, robot.leftOut);
  TEST_ASSERT_EQUAL(0, robot.rightOut);
}

void test_regular_heartbeats_keep_the_robot_moving() {
  Robot robot;
  robot.receive("h250\nc150,150\n");
  for (int i = 0; i < 15; i++) {
    robot.run(200);
    robot.receive("h250\n");
  }
  TEST_ASSERT_EQUAL(150, robot.leftOut);
  TEST_ASSERT_EQUAL(150, robot.rightOut);
}

void test_garbage_between_commands_does_not_move_the_robot() {
  Robot robot;
  robot.receive("c50,50\n");
  robot.receive("c999,999\nxyz\nc12\n");
  robot.run(2000);
  TEST_ASSERT_EQUAL(50, robot.leftOut);
  TEST_ASSERT_EQUAL(50, robot.rightOut);
}

void test_sonar_echo_becomes_an_app_line() {
  SonarFilter filter;
  char line[16];
  TEST_ASSERT_TRUE(formatSonar(line, sizeof(line), filter.add(echoUsToCm(580))));
  TEST_ASSERT_EQUAL_STRING("s10", line);
}

void test_sonar_timeout_reports_max_distance() {
  SonarFilter filter;
  char line[16];
  TEST_ASSERT_TRUE(formatSonar(line, sizeof(line), filter.add(echoUsToCm(0))));
  TEST_ASSERT_EQUAL_STRING("s300", line);
}

void test_hdc1080_reading_becomes_an_app_line() {
  char line[24];
  TEST_ASSERT_TRUE(formatEnv(line, sizeof(line), hdcTemperatureC(0x6000), hdcHumidityPct(0x8000)));
  TEST_ASSERT_EQUAL_STRING("e21.9,50.0", line);
}

void test_hdc1080_extremes_fit_the_line_buffer() {
  char line[24];
  TEST_ASSERT_TRUE(formatEnv(line, sizeof(line), hdcTemperatureC(0xFFFF), hdcHumidityPct(0xFFFF)));
  TEST_ASSERT_EQUAL_STRING("e125.0,100.0", line);
  TEST_ASSERT_TRUE(formatEnv(line, sizeof(line), hdcTemperatureC(0x0000), hdcHumidityPct(0x0000)));
  TEST_ASSERT_EQUAL_STRING("e-40.0,0.0", line);
}

void test_sonar_timeout_is_shorter_than_default_interval() {
  TEST_ASSERT_TRUE(SONAR_TIMEOUT_MS < SONAR_DEFAULT_INTERVAL_MS);
}

int main() {
  UNITY_BEGIN();
  RUN_TEST(test_control_command_drives_both_tracks_forward);
  RUN_TEST(test_spin_command_drives_tracks_in_opposite_directions);
  RUN_TEST(test_command_split_across_reads_is_applied_once_complete);
  RUN_TEST(test_silent_phone_stops_the_robot);
  RUN_TEST(test_regular_heartbeats_keep_the_robot_moving);
  RUN_TEST(test_garbage_between_commands_does_not_move_the_robot);
  RUN_TEST(test_sonar_echo_becomes_an_app_line);
  RUN_TEST(test_sonar_timeout_reports_max_distance);
  RUN_TEST(test_hdc1080_reading_becomes_an_app_line);
  RUN_TEST(test_hdc1080_extremes_fit_the_line_buffer);
  RUN_TEST(test_sonar_timeout_is_shorter_than_default_interval);
  return UNITY_END();
}
