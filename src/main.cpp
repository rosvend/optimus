#include <Arduino.h>
#include "ramp.h"

// L298N inputs (ENA/ENB jumpers on); both channels mirrored until we know which one is wired
const int CHANNELS[][2] = {{5, 6}, {7, 8}};
const int BUTTON_PIN = 41;

const int SPEED_STEP = 51;
const float ACCEL_PER_SECOND = 170.0f;
const unsigned long REVERSE_PAUSE_MS = 500;
const unsigned long LOOP_MS = 10;

SpeedRamp ramp(ACCEL_PER_SECOND, REVERSE_PAUSE_MS);

void drive(int speed) {
  int duty = abs(speed);
  for (auto &pins : CHANNELS) {
    analogWrite(pins[0], speed > 0 ? duty : 0);
    analogWrite(pins[1], speed < 0 ? duty : 0);
  }
}

void handleKey(char key) {
  int before = ramp.target();
  switch (key) {
    case 'w': ramp.setTarget(ramp.target() + SPEED_STEP); break;
    case 's': ramp.setTarget(ramp.target() - SPEED_STEP); break;
    case ' ':
    case 'x': ramp.setTarget(0); break;
    default: return;
  }
  if (ramp.target() != before) Serial.printf("target: %d\n", ramp.target());
}

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  drive(0);
  Serial.println("w = faster forward, s = faster backward, space/x/button = stop");
}

void loop() {
  while (Serial.available()) handleKey(Serial.read());
  if (digitalRead(BUTTON_PIN) == LOW) handleKey('x');

  drive(ramp.update(LOOP_MS));
  delay(LOOP_MS);
}
