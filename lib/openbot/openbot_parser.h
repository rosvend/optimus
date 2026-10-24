#pragma once

enum class MessageType { None, Control, Heartbeat, Feature, SonarInterval };

struct Message {
  MessageType type;
  int left;
  int right;
  long intervalMs;
};

// Parses OpenBot's newline-terminated lines: c<left>,<right>  h<ms>  f  s<ms>
class OpenBotParser {
public:
  Message feed(char c);

private:
  static const int MAX_LINE = 32;
  char line_[MAX_LINE];
  int length_ = 0;
  bool overflow_ = false;

  Message parse() const;
};
