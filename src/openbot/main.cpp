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
}

void loop() {
  while (Serial.available()) handle(parser.feed(Serial.read()));
  if (heartbeat.expired(LOOP_MS)) setTargets(0, 0);

  leftMotor.drive(leftRamp.update(LOOP_MS));
  rightMotor.drive(rightRamp.update(LOOP_MS));
  delay(LOOP_MS);
}
