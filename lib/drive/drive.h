#pragma once

struct Targets {
  int left;
  int right;
};

// Maps a key to new track targets: w/s forward/back, a/d spin, space/x stop.
Targets applyKey(Targets current, char key, int step);
