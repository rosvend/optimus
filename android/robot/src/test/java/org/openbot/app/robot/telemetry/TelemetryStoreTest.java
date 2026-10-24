package org.openbot.app.robot.telemetry;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import java.util.List;
import org.junit.Before;
import org.junit.Test;

public class TelemetryStoreTest {
  private TelemetryStore store;

  @Before
  public void setup() {
    store = new TelemetryStore(3);
  }

  private TelemetryReading reading(long timestampMs) {
    return new TelemetryReading(timestampMs, 20f + timestampMs, 50f, null, null);
  }

  @Test
  public void peekReturnsOldestFirstWithoutRemoving() {
    store.add(reading(1));
    store.add(reading(2));
    store.add(reading(3));

    List<TelemetryReading> batch = store.peek(2);
    assertEquals(2, batch.size());
    assertEquals(1, batch.get(0).timestampMs);
    assertEquals(2, batch.get(1).timestampMs);
    assertEquals(3, store.size());
  }

  @Test
  public void removeFirstDropsOldestReadings() {
    store.add(reading(1));
    store.add(reading(2));
    store.add(reading(3));

    store.removeFirst(2);

    List<TelemetryReading> remaining = store.peek(3);
    assertEquals(1, remaining.size());
    assertEquals(3, remaining.get(0).timestampMs);
  }

  @Test
  public void fullStoreDropsOldestReading() {
    store.add(reading(1));
    store.add(reading(2));
    store.add(reading(3));
    store.add(reading(4)); // capacity is 3

    assertEquals(3, store.size());
    List<TelemetryReading> remaining = store.peek(3);
    assertTrue(remaining.stream().allMatch(r -> r.timestampMs >= 2));
  }

  @Test
  public void removeFirstBeyondSizeIsSafe() {
    store.add(reading(1));
    store.removeFirst(5);
    assertEquals(0, store.size());
  }
}