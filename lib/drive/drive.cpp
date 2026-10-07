#include "drive.h"

const int MAX_SPEED = 255;

static int clampSpeed(int speed) {
  if (speed > MAX_SPEED) return MAX_SPEED;
  if (speed < -MAX_SPEED) return -MAX_SPEED;
  return speed;
}

Targets applyKey(Targets t, char key, int step) {
  switch (key) {
    case 'w': t.left += step; t.right += step; break;
    case 's': t.left -= step; t.right -= step; break;
    case 'a': t.left -= step; t.right += step; break;
    case 'd': t.left += step; t.right -= step; break;
    case ' ':
    case 'x': return {0, 0};
  }
  return {clampSpeed(t.left), clampSpeed(t.right)};
}
