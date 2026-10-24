#pragma once

// Builds OpenBot vehicle->app lines (without the trailing newline).
// Each returns false if the line did not fit; buf is always terminated.
bool formatSonar(char *buf, int size, long cm);
bool formatEnv(char *buf, int size, float tempC, float humPct);
bool formatFeatures(char *buf, int size, const char *robotType);
