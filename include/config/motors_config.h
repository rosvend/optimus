#pragma once

// T-Beam GPIOs wired to the L298N IN pins (ENA/ENB jumpers on).
// Not 32/33: on the T-Beam v1.x those are wired to the LoRa radio (DIO1/DIO2 or BUSY).
// GPIO 2 is pulled low at boot, so the motors stay still while the ESP32 starts.
// Swap a pair's pins if that track spins the wrong way
const int LEFT_MOTOR_FORWARD_PIN = 25;
const int LEFT_MOTOR_BACKWARD_PIN = 4;
const int RIGHT_MOTOR_FORWARD_PIN = 13;
const int RIGHT_MOTOR_BACKWARD_PIN = 2;
