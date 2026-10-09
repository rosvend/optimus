#include "openbot_parser.h"
#include <stdlib.h>

static const Message NO_MESSAGE = {MessageType::None, 0, 0, 0};
static const long MAX_TARGET = 255;

static bool readNumber(const char *text, long &value, const char *&end) {
  char *stop;
  value = strtol(text, &stop, 10);
  end = stop;
  return stop != text;
}

static bool inRange(long value) { return value >= -MAX_TARGET && value <= MAX_TARGET; }

Message OpenBotParser::feed(char c) {
  if (c == '\r') return NO_MESSAGE;

  if (c != '\n') {
    if (length_ < MAX_LINE - 1) line_[length_++] = c;
    else overflow_ = true;
    return NO_MESSAGE;
  }

  line_[length_] = '\0';
  Message message = overflow_ ? NO_MESSAGE : parse();
  length_ = 0;
  overflow_ = false;
  return message;
}

Message OpenBotParser::parse() const {
  if (length_ == 0) return NO_MESSAGE;

  const char *body = line_ + 1;
  switch (line_[0]) {
    case 'c': {
      long left, right;
      const char *end;
      if (!readNumber(body, left, end) || *end != ',') return NO_MESSAGE;
      if (!readNumber(end + 1, right, end) || *end != '\0') return NO_MESSAGE;
      if (!inRange(left) || !inRange(right)) return NO_MESSAGE;
      return {MessageType::Control, (int)left, (int)right, 0};
    }
    case 'h': {
      long interval;
      const char *end;
      if (!readNumber(body, interval, end) || *end != '\0' || interval < 0) return NO_MESSAGE;
      return {MessageType::Heartbeat, 0, 0, interval};
    }
    case 'f': return {MessageType::Feature, 0, 0, 0};
    default: return NO_MESSAGE;
  }
}
