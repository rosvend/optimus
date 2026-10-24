package org.openbot.app.robot.telemetry;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import com.google.gson.JsonArray;
import com.google.gson.JsonParser;
import java.io.IOException;
import java.util.List;
import okhttp3.OkHttpClient;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import okhttp3.mockwebserver.RecordedRequest;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

public class TelemetryClientTest {
  private MockWebServer server;
  private TelemetryClient client;

  @Before
  public void setUp() throws IOException {
    server = new MockWebServer();
    server.start();
    client = new TelemetryClient(new OkHttpClient());
  }

  @After
  public void tearDown() throws IOException {
    server.shutdown();
  }

  private List<TelemetryReading> sampleBatch() {
    return List.of(
        new TelemetryReading(1000, 23.4f, 61.2f, 6.2442, -75.5812),
        new TelemetryReading(2000, 22.5f, 60f, null, null));
  }

  @Test
  public void successfulUploadSendsApiKeyAndPayload() throws InterruptedException {
    server.enqueue(new MockResponse().setBody("{\"stored\":4}"));

    assertTrue(client.upload(server.url("/").toString(), "test-key", sampleBatch(), 5000));

    RecordedRequest request = server.takeRequest();
    assertEquals("POST", request.getMethod());
    assertEquals("test-key", request.getHeader("x-api-key"));
    assertEquals("application/json; charset=utf-8", request.getHeader("content-type"));

    JsonArray readings =
        JsonParser.parseString(request.getBody().readUtf8())
            .getAsJsonObject()
            .get("readings")
            .getAsJsonArray();
    assertEquals(2, readings.size());
    assertEquals(4000, readings.get(0).getAsJsonObject().get("age_ms").getAsLong());
  }

  @Test
  public void unauthorizedUploadFails() {
    server.enqueue(new MockResponse().setResponseCode(401));

    assertFalse(client.upload(server.url("/").toString(), "bad-key", sampleBatch(), 5000));
  }

  @Test
  public void serverErrorFails() {
    server.enqueue(new MockResponse().setResponseCode(500));

    assertFalse(client.upload(server.url("/").toString(), "test-key", sampleBatch(), 5000));
  }

  @Test
  public void unreachableServerFails() throws IOException {
    String url = server.url("/").toString();
    server.shutdown();

    assertFalse(client.upload(url, "test-key", sampleBatch(), 5000));
  }
}