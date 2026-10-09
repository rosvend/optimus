#include <Arduino.h>
#include "config/controls_config.h"
#include "config/motors_config.h"
#include "config/openbot_config.h"
#include "config/ramp_config.h"
#include "heartbeat.h"
#include "motor.h"
#include "openbot_parser.h"
#include "ramp.h"

Motor leftMotor(LEFT_MOTOR_FORWARD_PIN, LEFT_MOTOR_BACKWARD_PIN);
Motor rightMotor(RIGHT_MOTOR_FORWARD_PIN, RIGHT_MOTOR_BACKWARD_PIN);
SpeedRamp leftRamp(ACCEL_PER_SECOND, REVERSE_PAUSE_MS);
SpeedRamp rightRamp(ACCEL_PER_SECOND, REVERSE_PAUSE_MS);
OpenBotParser parser;
Heartbeat heartbeat;
unsigned long lastLoopMs = 0;

void setTargets(int left, int right) {
  leftRamp.setTarget(left);
  rightRamp.setTarget(right);
}

void handle(const Message &message) {
  switch (message.type) {
    case MessageType::Control: setTargets(message.left, message.right); break;
    case MessageType::Heartbeat: heartbeat.beat(message.intervalMs); break;
    case MessageType::Feature: Serial.printf("f%s:\n", ROBOT_TYPE); break;
    default: break;
  }
}

void setup() {
  Serial.begin(SERIAL_BAUD);
  leftMotor.drive(0);
  rightMotor.drive(0);
  Serial.println('r');
  lastLoopMs = millis();
}

void loop() {
  for (int i = 0; i < MAX_SERIAL_BYTES_PER_LOOP && Serial.available(); i++) {
    handle(parser.feed(Serial.read()));
  }

  unsigned long now = millis();
  unsigned long elapsedMs = now - lastLoopMs;
  lastLoopMs = now;

  if (heartbeat.expired(elapsedMs)) setTargets(0, 0);
  leftMotor.drive(leftRamp.update(elapsedMs));
  rightMotor.drive(rightRamp.update(elapsedMs));
  delay(LOOP_MS);
}
