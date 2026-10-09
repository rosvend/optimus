# Optimus Hardware Components Specification

This document details the hardware components, electrical specifications, and wiring layout for the tracked autonomous mini vehicle. This specification serves as reference documentation for firmware development and motion control integration.

---

## 1. Primary Components Overview

| Category | Component Description | Model / Specifications | Quantity |
| :--- | :--- | :--- | :---: |
| **Main Controller** | Microcontroller Unit | LilyGO T-Beam v1 with AXP2101 PMU (ESP32, LoRa, GPS) | 1 |
| **Phone Link** | USB OTG cable | Android phone running the OpenBot app (`android/`) | 1 |
| **Environment Sensor** | Temperature & Humidity | TI HDC1080 (I2C, 0x40) | 1 |
| **Motor Driver** | Dual H-Bridge Module | L298N Stepper / DC Motor Driver (Red Board) | 1 |
| **Drive Actuators** | Geared DC Motors | 33GB-520 High-Torque DC Motors (12V, 350 RPM ±10%) | 2 |
| **Pan Servo** | Micro Servo Motor | SG90 9g Micro Servo | 1 |
| **Ranging Sensor** | Ultrasonic Distance Module | HC-SR04 (5V, trigger/echo) | 1 |
| **Power Supply** | Li-ion Battery Array | 18650 3.7V 2500mAh Rechargeable Batteries | 4 |
| **Power Control** | Master Power Toggle | SPST Heavy-Duty Toggle Switch | 1 |
| **Antenna** | Wireless Range Extension | External Wi-Fi / Bluetooth Antenna & Base Module | 1 |
| **Chassis Structure**| Tracked Chassis | 4-Track Continuous Tread Metal Assembly with Springs | 1 |
| **Structural Plates**| Mounting Baseboard | Plywood Mounting Plates & Aluminum Frame Bracket | 1 |

---

## 2. Comprehensive Hardware Breakdown

### 2.1 Microcontroller Unit
* **Model:** LilyGO T-Beam v1 (AXP2101 PMU)
* **Processor:** ESP32 (Dual-core Xtensa LX6 @ 240 MHz, Wi-Fi & Bluetooth)
* **Onboard Features:** AXP2101 power management, LoRa radio, GPS, user button (GPIO 38), USB-UART bridge. LoRa, GPS and the PMU are not used by the firmware; the AXP2101 defaults keep the ESP32 and the 3.3V header rail powered.
* **Role:** Drives the L298N, reads the HC-SR04 and HDC1080, and talks to the OpenBot Android app over USB serial (115200 baud, OTG cable). The phone powers the T-Beam through USB.

### 2.1.1 Wiring Rules
* **The HC-SR04 ECHO pin outputs 5V:** it must go through a divider (e.g. 1 kΩ / 2 kΩ) before GPIO 39.
* The HC-SR04 takes 5V from the L298N 5V output.
* T-Beam, L298N and HC-SR04 grounds are tied together.
* The HDC1080 runs from the T-Beam 3.3V rail on the shared I2C bus (AXP2101 is at 0x34).

### 2.2 Motor Driver & Actuators
* **L298N Dual H-Bridge Driver:**
  * **Operating Voltage:** 5V to 35V DC
  * **Peak Output Current:** 2A per channel
  * **Controls:** 4 Directional Inputs (`IN1`, `IN2`, `IN3`, `IN4`) + 2 Speed Control Enables (`ENA`, `ENB`).
* **33GB-520 DC Motors:**
  * **Voltage Rating:** 12V DC
  * **Rated Speed:** 350 RPM ±10%
  * **Configuration:** Drives left and right continuous tracks for differential skid-steering.

### 2.3 Sensor & Pan System
* **RCWL-9610 Ultrasonic Proximity Sensor:**
  * **Ranging Range:** 2 cm to 450 cm
  * **Supported Modes:** GPIO trigger/echo, I2C, UART, 1-Wire
  * **Mounting:** Positioned at the front front-facing platform.
* **SG90 Micro Servo:**
  * **Operating Voltage:** 4.8V – 6.0V
  * **Rotation Range:** ~180°
  * **Function:** Pans the ultrasonic sensor horizontally for obstacle detection and environment mapping.

### 2.4 Power Management
* **18650 Battery Array:** 4-cell battery holder configured to supply high-current ~12V power to the L298N driver board and step-down power to logic circuits.
* **Master Power Switch:** Single Pole Single Throw (SPST) toggle switch wired directly into the main power line for system safety and isolation.

---

## 3. General Pinout Map for Firmware Configuration

> **Note:** GPIO 32/33 are not used because the T-Beam v1.x wires them to the LoRa radio. Confirm these GPIOs against the silkscreen of your T-Beam revision before wiring. The values live in `include/config/`.

| Component                 | T-Beam GPIO | Notes                                  |
|---------------------------|-------------|----------------------------------------|
| Motor Driver IN1 / IN2    | 25 / 4      | Left track, PWM                        |
| Motor Driver IN3 / IN4    | 13 / 2      | Right track, PWM                       |
| Motor Driver ENA / ENB    | —           | Jumpers on; speed is PWM on the IN pins |
| Ultrasonic Sensor Trigger | 14          | 3.3V output                            |
| Ultrasonic Sensor Echo    | 39          | Input-only pin, through a 5V → 3.3V divider |
| HDC1080 SDA / SCL         | 21 / 22     | Shared with the AXP2101                |
| Stop Button               | 38          | On-board user button                   |