# Optimus Hardware Components Specification

This document details the hardware components, electrical specifications, and wiring layout for the tracked autonomous mini vehicle. This specification serves as reference documentation for firmware development and motion control integration.

---

## 1. Primary Components Overview

| Category | Component Description | Model / Specifications | Quantity |
| :--- | :--- | :--- | :---: |
| **Main Controller** | Microcontroller Unit | M5Stack AtomS3 (ESP32-S3, 0.85" LCD, 6-DOF IMU) | 1 |
| **Motor Driver** | Dual H-Bridge Module | L298N Stepper / DC Motor Driver (Red Board) | 1 |
| **Drive Actuators** | Geared DC Motors | 33GB-520 High-Torque DC Motors (12V, 350 RPM ±10%) | 2 |
| **Pan Servo** | Micro Servo Motor | SG90 9g Micro Servo | 1 |
| **Ranging Sensor** | Ultrasonic Distance Module | RCWL-9610 (Supports GPIO, I2C, UART, 1-Wire) | 1 |
| **Power Supply** | Li-ion Battery Array | 18650 3.7V 2500mAh Rechargeable Batteries | 4 |
| **Power Control** | Master Power Toggle | SPST Heavy-Duty Toggle Switch | 1 |
| **Antenna** | Wireless Range Extension | External Wi-Fi / Bluetooth Antenna & Base Module | 1 |
| **Chassis Structure**| Tracked Chassis | 4-Track Continuous Tread Metal Assembly with Springs | 1 |
| **Structural Plates**| Mounting Baseboard | Plywood Mounting Plates & Aluminum Frame Bracket | 1 |

---

## 2. Comprehensive Hardware Breakdown

### 2.1 Microcontroller Unit
* **Model:** M5Stack AtomS3
* **Processor:** ESP32-S3FN8 (Dual-core Xtensa LX7 @ 240 MHz, Wi-Fi & Bluetooth 5 LE)
* **Onboard Features:** 0.85-inch IPS Color LCD Screen, 6-Axis IMU (MPU6886), Programmable Button, USB-C Interface
* **Role:** Central processing unit responsible for sensor data processing, motion logic calculation, PWM output to the motor driver, and wireless telemetry communication.

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

> **Note:** Update the pin assignments below based on the final physical GPIO connections on the AtomS3 expansion header.

| Component                 | AtomS3 Pin Connection            |
|---------------------------|----------------------------------|
| Motor Driver IN1 / IN2    | GPIO Pin (Left Motor Direction)  |
| Motor Driver IN3 / IN4    | GPIO Pin (Right Motor Direction) |
| Motor Driver ENA / ENB    | PWM Capable Pins (Speed Control) |
| Ultrasonic Sensor Trigger | GPIO Output                      |
| Ultrasonic Sensor Echo    | GPIO Input                       |
| SG90 Servo Signal         | PWM Capable Pin                  |