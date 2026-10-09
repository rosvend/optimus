#pragma once
#include <stdint.h>

// HDC1080 raw 16-bit register values to physical units (datasheet section 8.6).
float hdcTemperatureC(uint16_t raw);
float hdcHumidityPct(uint16_t raw);
