#include "hdc1080.h"

float hdcTemperatureC(uint16_t raw) { return raw / 65536.0f * 165.0f - 40.0f; }

float hdcHumidityPct(uint16_t raw) { return raw / 65536.0f * 100.0f; }
