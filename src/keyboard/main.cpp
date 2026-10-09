#include <Arduino.h>
#include "config/controls_config.h"
#include "config/motors_config.h"
#include "config/ramp_config.h"
#include "drive.h"
#include "motor.h"
#include "ramp.h"

Motor leftMotor(LEFT_MOTOR_FORWARD_PIN, LEFT_MOTOR_BACKWARD_PIN);
Motor rightMotor(RIGHT_MOTOR_FORWARD_PIN, RIGHT_MOTOR_BACKWARD_PIN);
SpeedRamp leftRamp(ACCEL_PER_SECOND, REVERSE_PAUSE_MS);
SpeedRamp rightRamp(ACCEL_PER_SECOND, REVERSE_PAUSE_MS);
Targets targets = {0, 0};

void handleKey(char key) {
  Targets next = applyKey(targets, key, SPEED_STEP);
  if (next.left == targets.left && next.right == targets.right) return;

  targets = next;
  leftRamp.setTarget(targets.left);
  rightRamp.setTarget(targets.right);
  Serial.printf("left: %d  right: %d\n", targets.left, targets.right);
}

void setup() {
  Serial.begin(SERIAL_BAUD);
  pinMode(STOP_BUTTON_PIN, INPUT_PULLUP);
  leftMotor.drive(0);
  rightMotor.drive(0);
  Serial.println("w/s = forward/backward, a/d = spin left/right, space/x/button = stop");
}

void loop() {
  while (Serial.available()) handleKey(Serial.read());
  if (digitalRead(STOP_BUTTON_PIN) == LOW) handleKey('x');

  leftMotor.drive(leftRamp.update(LOOP_MS));
  rightMotor.drive(rightRamp.update(LOOP_MS));
  delay(LOOP_MS);
}
