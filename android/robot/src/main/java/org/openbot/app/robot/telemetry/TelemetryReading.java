package org.openbot.app.robot.telemetry;

/**
 * One environment sensor capture, ready to be buffered and uploaded.
 *
 * <p>Temperature and humidity come from the HDC1080 via the serial link, lat/lon from the phone
 * GPS. Lat/lon are null while there is no fix (the API requires both or neither).
 */
public final class TelemetryReading {
  public final long timestampMs;
  public final Float temperature;
  public final Float humidity;
  public final Double lat;
  public final Double lon;

  public TelemetryReading(
      long timestampMs, Float temperature, Float humidity, Double lat, Double lon) {
    this.timestampMs = timestampMs;
    this.temperature = temperature;
    this.humidity = humidity;
    this.lat = lat;
    this.lon = lon;
  }
}