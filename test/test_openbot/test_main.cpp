#include <string.h>
#include <unity.h>
#include "openbot_parser.h"

Message feedLine(OpenBotParser &parser, const char *line) {
  Message last = {MessageType::None, 0, 0, 0};
  for (const char *c = line; *c; c++) last = parser.feed(*c);
  return last;
}

void test_incomplete_line_yields_nothing() {
  OpenBotParser parser;
  TEST_ASSERT_EQUAL(MessageType::None, (int)feedLine(parser, "c10,20").type);
}

void test_control_message() {
  OpenBotParser parser;
  Message m = feedLine(parser, "c100,-50\n");
  TEST_ASSERT_EQUAL(MessageType::Control, (int)m.type);
  TEST_ASSERT_EQUAL(100, m.left);
  TEST_ASSERT_EQUAL(-50, m.right);
}

void test_heartbeat_message() {
  OpenBotParser parser;
  Message m = feedLine(parser, "h250\n");
  TEST_ASSERT_EQUAL(MessageType::Heartbeat, (int)m.type);
  TEST_ASSERT_EQUAL(250, m.intervalMs);
}

void test_feature_request() {
  OpenBotParser parser;
  TEST_ASSERT_EQUAL(MessageType::Feature, (int)feedLine(parser, "f\n").type);
}

void test_carriage_return_is_ignored() {
  OpenBotParser parser;
  Message m = feedLine(parser, "c1,2\r\n");
  TEST_ASSERT_EQUAL(MessageType::Control, (int)m.type);
  TEST_ASSERT_EQUAL(2, m.right);
}

void test_unknown_header_is_ignored() {
  OpenBotParser parser;
  TEST_ASSERT_EQUAL(MessageType::None, (int)feedLine(parser, "l10,10\n").type);
}

void test_malformed_control_is_ignored() {
  OpenBotParser parser;
  TEST_ASSERT_EQUAL(MessageType::None, (int)feedLine(parser, "c100\n").type);
}

void test_parser_recovers_after_bad_line() {
  OpenBotParser parser;
  feedLine(parser, "zzz\n");
  TEST_ASSERT_EQUAL(MessageType::Control, (int)feedLine(parser, "c5,6\n").type);
}

void test_oversized_line_is_dropped_then_recovers() {
  OpenBotParser parser;
  char longLine[200];
  memset(longLine, '1', sizeof(longLine));
  longLine[0] = 'c';
  longLine[198] = '\n';
  longLine[199] = '\0';
  TEST_ASSERT_EQUAL(MessageType::None, (int)feedLine(parser, longLine).type);
  TEST_ASSERT_EQUAL(MessageType::Control, (int)feedLine(parser, "c5,6\n").type);
}

int main() {
  UNITY_BEGIN();
  RUN_TEST(test_incomplete_line_yields_nothing);
  RUN_TEST(test_control_message);
  RUN_TEST(test_heartbeat_message);
  RUN_TEST(test_feature_request);
  RUN_TEST(test_carriage_return_is_ignored);
  RUN_TEST(test_unknown_header_is_ignored);
  RUN_TEST(test_malformed_control_is_ignored);
  RUN_TEST(test_parser_recovers_after_bad_line);
  RUN_TEST(test_oversized_line_is_dropped_then_recovers);
  return UNITY_END();
}
