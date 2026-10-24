#pragma once

// HC-SR04: ECHO is 5 V, so it goes through a divider to 3.3 V.
// GPIO 39 is input-only, which is all ECHO needs.
const int SONAR_TRIG_PIN = 14;
const int SONAR_ECHO_PIN = 39;
const unsigned long SONAR_DEFAULT_INTERVAL_MS = 100;
const unsigned long SONAR_TIMEOUT_MS = 30;

// HDC1080 shares the T-Beam's I2C bus with the AXP2101 (0x34).
const int I2C_SDA_PIN = 21;
const int I2C_SCL_PIN = 22;
const int HDC1080_ADDR = 0x40;
const unsigned long HDC1080_CONVERSION_MS = 20;
const unsigned long ENV_INTERVAL_MS = 2000;
