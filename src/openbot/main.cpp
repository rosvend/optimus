#include <Arduino.h>
#include <Wire.h>
#include "config/controls_config.h"
#include "config/motors_config.h"
#include "config/openbot_config.h"
#include "config/ramp_config.h"
#include "config/sensors_config.h"
#include "hdc1080.h"
#include "heartbeat.h"
#include "motor.h"
#include "openbot_parser.h"
#include "ramp.h"
#include "sonar.h"
#include "telemetry.h"

// Serial is the link to the OpenBot app: only protocol lines may be written to it.

Motor leftMotor(LEFT_MOTOR_FORWARD_PIN, LEFT_MOTOR_BACKWARD_PIN);
Motor rightMotor(RIGHT_MOTOR_FORWARD_PIN, RIGHT_MOTOR_BACKWARD_PIN);
SpeedRamp leftRamp(ACCEL_PER_SECOND, REVERSE_PAUSE_MS);
SpeedRamp rightRamp(ACCEL_PER_SECOND, REVERSE_PAUSE_MS);
OpenBotParser parser;
Heartbeat heartbeat;
SonarFilter sonarFilter;

unsigned long sonarIntervalMs = SONAR_DEFAULT_INTERVAL_MS;
unsigned long lastPingMs = 0;
bool pingPending = false;

volatile unsigned long echoStartUs = 0;
volatile unsigned long echoDurationUs = 0;
volatile bool echoDone = false;

bool envConverting = false;
unsigned long envStartMs = 0;
unsigned long lastEnvMs = 0;

void sendLine(const char *line) {
  Serial.print(line);
  Serial.print('\n');
}

void IRAM_ATTR onEcho() {
  if (digitalRead(SONAR_ECHO_PIN) == HIGH) {
    echoStartUs = micros();
  } else {
    echoDurationUs = micros() - echoStartUs;
    echoDone = true;
  }
}

void setTargets(int left, int right) {
  leftRamp.setTarget(left);
  rightRamp.setTarget(right);
}

void sendFeatures() {
  char line[32];
  if (formatFeatures(line, sizeof(line), ROBOT_TYPE)) sendLine(line);
}

void handle(const Message &message) {
  switch (message.type) {
    case MessageType::Control: setTargets(message.left, message.right); break;
    case MessageType::Heartbeat: heartbeat.beat(message.intervalMs); break;
    case MessageType::Feature: sendFeatures(); break;
    case MessageType::SonarInterval:
      sonarIntervalMs = max((unsigned long)message.intervalMs, SONAR_TIMEOUT_MS);
      break;
    default: break;
  }
}

void reportSonar(unsigned long echoUs) {
  char line[16];
  if (formatSonar(line, sizeof(line), sonarFilter.add(echoUsToCm(echoUs)))) sendLine(line);
}

// Fires TRIG every sonarIntervalMs; the echo is timed by onEcho() so the loop never blocks.
void updateSonar(unsigned long now) {
  if (pingPending) {
    if (echoDone) {
      pingPending = false;
      reportSonar(echoDurationUs);
    } else if (now - lastPingMs >= SONAR_TIMEOUT_MS) {
      pingPending = false;
      reportSonar(0);
    }
    return;
  }
  if (now - lastPingMs < sonarIntervalMs) return;

  echoDone = false;
  digitalWrite(SONAR_TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(SONAR_TRIG_PIN, LOW);
  lastPingMs = now;
  pingPending = true;
}

void configureHdc1080() {
  Wire.beginTransmission(HDC1080_ADDR);
  Wire.write(0x02);  // configuration register
  Wire.write(0x10);  // sequential temperature + humidity, 14 bit
  Wire.write(0x00);
  Wire.endTransmission();
}

// Two steps so the loop never waits: trigger a conversion, read it on a later pass.
void updateEnv(unsigned long now) {
  if (!envConverting) {
    if (now - lastEnvMs < ENV_INTERVAL_MS) return;
    lastEnvMs = now;
    Wire.beginTransmission(HDC1080_ADDR);
    Wire.write(0x00);  // temperature register starts a conversion
    envConverting = Wire.endTransmission() == 0;
    envStartMs = now;
    return;
  }
  if (now - envStartMs < HDC1080_CONVERSION_MS) return;
  envConverting = false;

  if (Wire.requestFrom(HDC1080_ADDR, 4) != 4) return;
  // One read per statement: the evaluation order of `a << 8 | b` is unspecified.
  uint16_t rawTemp = Wire.read() << 8;
  rawTemp |= Wire.read();
  uint16_t rawHum = Wire.read() << 8;
  rawHum |= Wire.read();

  char line[24];
  if (formatEnv(line, sizeof(line), hdcTemperatureC(rawTemp), hdcHumidityPct(rawHum))) sendLine(line);
}

void setup() {
  Serial.begin(SERIAL_BAUD);
  leftMotor.drive(0);
  rightMotor.drive(0);

  pinMode(SONAR_TRIG_PIN, OUTPUT);
  digitalWrite(SONAR_TRIG_PIN, LOW);
  pinMode(SONAR_ECHO_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(SONAR_ECHO_PIN), onEcho, CHANGE);

  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  configureHdc1080();

  sendLine("r");
}

void loop() {
  while (Serial.available()) handle(parser.feed(Serial.read()));
  if (heartbeat.expired(LOOP_MS)) setTargets(0, 0);

  unsigned long now = millis();
  updateSonar(now);
  updateEnv(now);

  leftMotor.drive(leftRamp.update(LOOP_MS));
  rightMotor.drive(rightRamp.update(LOOP_MS));
  delay(LOOP_MS);
}
