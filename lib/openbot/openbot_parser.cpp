#include "openbot_parser.h"
#include <stdlib.h>

static const Message NO_MESSAGE = {MessageType::None, 0, 0, 0};

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
      char *comma;
      long left = strtol(body, &comma, 10);
      if (*comma != ',') return NO_MESSAGE;
      long right = strtol(comma + 1, nullptr, 10);
      return {MessageType::Control, (int)left, (int)right, 0};
    }
    case 'h': return {MessageType::Heartbeat, 0, 0, atol(body)};
    case 'f': return {MessageType::Feature, 0, 0, 0};
    case 's': return {MessageType::SonarInterval, 0, 0, atol(body)};
    default: return NO_MESSAGE;
  }
}
