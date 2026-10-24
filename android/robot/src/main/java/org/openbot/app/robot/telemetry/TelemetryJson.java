package org.openbot.app.robot.telemetry;

import com.google.gson.Gson;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Builds the JSON body expected by the telemetry Lambda (see infra/README.md):
 *
 * <pre>{@code
 * {"device":"optimus","readings":[{"age_ms":1200,"temperature":23.4,"humidity":55.1,"lat":6.24,"lon":-75.58}]}
 * }</pre>
 *
 * {@code age_ms} keeps the real capture time of buffered readings, so the server timestamps them
 * correctly even after retries. Sensor fields that are unknown stay out of the JSON.
 */
public final class TelemetryJson {
  public static final String DEFAULT_DEVICE = "optimus";

  private static final Gson GSON = new Gson();

  private TelemetryJson() {}

  public static String build(String device, List<TelemetryReading> readings, long nowMs) {
    List<Map<String, Object>> items = new ArrayList<>(readings.size());
    for (TelemetryReading reading : readings) {
      Map<String, Object> item = new LinkedHashMap<>();
      item.put("age_ms", Math.max(0L, nowMs - reading.timestampMs));
      if (reading.temperature != null) {
        item.put("temperature", reading.temperature);
      }
      if (reading.humidity != null) {
        item.put("humidity", reading.humidity);
      }
      if (reading.lat != null && reading.lon != null) {
        item.put("lat", reading.lat);
        item.put("lon", reading.lon);
      }
      items.add(item);
    }
    Map<String, Object> payload = new LinkedHashMap<>();
    payload.put("device", device == null || device.isEmpty() ? DEFAULT_DEVICE : device);
    payload.put("readings", items);
    return GSON.toJson(payload);
  }
}