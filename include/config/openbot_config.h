#pragma once

// Name the app shows for the robot
const char ROBOT_TYPE[] = "OPTIMUS";

// Cap per loop so a flood of serial data can't delay the watchdog
const int MAX_SERIAL_BYTES_PER_LOOP = 64;
