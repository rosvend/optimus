package org.openbot.app.robot.telemetry;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.util.Arrays;
import java.util.List;
import org.junit.Test;

public class TelemetryJsonTest {

  private static JsonObject parse(String json) {
    return JsonParser.parseString(json).getAsJsonObject();
  }

  @Test
  public void payloadMatchesIngestApiFormat() {
    long now = 1_000_000L;
    TelemetryReading reading =
        new TelemetryReading(now - 1200, 23.4f, 61.2f, 6.2442, -75.5812);

    JsonObject payload = parse(TelemetryJson.build("optimus", List.of(reading), now));

    assertEquals("optimus", payload.get("device").getAsString());
    JsonArray readings = payload.get("readings").getAsJsonArray();
    assertEquals(1, readings.size());
    JsonObject item = readings.get(0).getAsJsonObject();
    assertEquals(1200, item.get("age_ms").getAsLong());
    assertEquals(23.4, item.get("temperature").getAsDouble(), 1e-6);
    assertEquals(61.2, item.get("humidity").getAsDouble(), 1e-6);
    assertEquals(6.2442, item.get("lat").getAsDouble(), 1e-6);
    assertEquals(-75.5812, item.get("lon").getAsDouble(), 1e-6);
  }

  @Test
  public void missingGpsFixOmitsLatLon() {
    long now = 1_000_000L;
    TelemetryReading reading = new TelemetryReading(now, 22.5f, 60f, null, null);

    JsonObject item =
        parse(TelemetryJson.build(null, List.of(reading), now))
            .get("readings")
            .getAsJsonArray()
            .get(0)
            .getAsJsonObject();

    assertFalse(item.has("lat"));
    assertFalse(item.has("lon"));
    assertEquals(22.5, item.get("temperature").getAsDouble(), 1e-6);
    assertEquals(60.0, item.get("humidity").getAsDouble(), 1e-6);
  }

  @Test
  public void futureTimestampsClampAgeToZero() {
    long now = 1_000_000L;
    TelemetryReading reading = new TelemetryReading(now + 5000, 22.5f, 60f, null, null);

    String json = TelemetryJson.build("optimus", List.of(reading), now);

    JsonObject item = parse(json).get("readings").getAsJsonArray().get(0).getAsJsonObject();
    assertEquals(0, item.get("age_ms").getAsLong());
  }

  @Test
  public void emptyDeviceFallsBackToOptimus() {
    JsonObject payload =
        parse(
            TelemetryJson.build(
                "", List.of(new TelemetryReading(0, 1f, 2f, null, null)), 0));

    assertEquals("optimus", payload.get("device").getAsString());
  }

  @Test
  public void batchesKeepTheirOrder() {
    long now = 10_000L;
    List<TelemetryReading> readings =
        Arrays.asList(
            new TelemetryReading(now - 1000, 1f, 2f, null, null),
            new TelemetryReading(now - 500, 3f, 4f, null, null));

    JsonArray items = parse(TelemetryJson.build(null, readings, now)).get("readings").getAsJsonArray();

    assertEquals(2, items.size());
    assertTrue(items.get(0).getAsJsonObject().has("temperature"));
    assertEquals(1000, items.get(0).getAsJsonObject().get("age_ms").getAsLong());
    assertEquals(500, items.get(1).getAsJsonObject().get("age_ms").getAsLong());
  }
}