package org.openbot.app.robot.telemetry;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.List;

/**
 * Bounded in-memory buffer of readings, oldest first. When the buffer is full the oldest reading
 * is dropped, so long offline stretches cannot exhaust memory.
 */
public final class TelemetryStore {
  private final int capacity;
  private final ArrayDeque<TelemetryReading> queue = new ArrayDeque<>();

  public TelemetryStore(int capacity) {
    this.capacity = capacity;
  }

  public synchronized void add(TelemetryReading reading) {
    if (queue.size() >= capacity) {
      queue.pollFirst();
    }
    queue.addLast(reading);
  }

  /** Returns up to {@code max} oldest readings without removing them. */
  public synchronized List<TelemetryReading> peek(int max) {
    List<TelemetryReading> batch = new ArrayList<>();
    for (TelemetryReading reading : queue) {
      if (batch.size() >= max) {
        break;
      }
      batch.add(reading);
    }
    return batch;
  }

  public synchronized void removeFirst(int count) {
    for (int i = 0; i < count && !queue.isEmpty(); i++) {
      queue.pollFirst();
    }
  }

  public synchronized int size() {
    return queue.size();
  }
}