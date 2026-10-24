package org.openbot.app.robot.telemetry;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;

import android.content.Context;
import android.content.SharedPreferences;
import androidx.preference.PreferenceManager;
import androidx.test.core.app.ApplicationProvider;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import com.google.gson.JsonArray;
import com.google.gson.JsonParser;
import java.io.IOException;
import okhttp3.OkHttpClient;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import okhttp3.mockwebserver.RecordedRequest;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;

@RunWith(AndroidJUnit4.class)
public class TelemetryManagerTest {
  private static final String URL_KEY = "telemetry_url";
  private static final String API_KEY_KEY = "telemetry_api_key";
  private static final String ENABLED_KEY = "telemetry_enabled";

  private MockWebServer server;
  private TelemetryStore store;
  private TelemetryManager manager;
  private SharedPreferences preferences;

  @Before
  public void setUp() throws IOException {
    server = new MockWebServer();
    server.start();

    Context context = ApplicationProvider.getApplicationContext();
    preferences = PreferenceManager.getDefaultSharedPreferences(context);
    preferences
        .edit()
        .putString(URL_KEY, server.url("/").toString())
        .putString(API_KEY_KEY, "test-key")
        .putBoolean(ENABLED_KEY, true)
        .apply();

    store = new TelemetryStore(100);
    manager =
        new TelemetryManager(
            context, store, new TelemetryClient(new OkHttpClient()), new LiveLocation());
  }

  @After
  public void tearDown() throws IOException {
    server.shutdown();
  }

  @Test
  public void bufferedReadingsAreUploadedAndCleared() throws InterruptedException {
    server.enqueue(new MockResponse().setBody("{\"stored\":4}"));

    manager.onEnvReading(23.4f, 61.2f);
    manager.onEnvReading(24.0f, 62.0f);
    manager.flush();

    assertEquals(0, store.size());

    RecordedRequest request = server.takeRequest();
    assertEquals("test-key", request.getHeader("x-api-key"));
    JsonArray readings =
        JsonParser.parseString(request.getBody().readUtf8())
            .getAsJsonObject()
            .get("readings")
            .getAsJsonArray();
    assertEquals(2, readings.size());
    // Robolectric grants no location permission, so readings carry temperature and humidity only.
    assertFalse(
        readings.get(0).getAsJsonObject().has("lat")
            || readings.get(0).getAsJsonObject().has("lon"));
  }

  @Test
  public void failedUploadKeepsReadingsBufferedForRetry() throws InterruptedException {
    server.enqueue(new MockResponse().setResponseCode(500));

    manager.onEnvReading(23.4f, 61.2f);
    manager.flush();
    assertEquals(1, store.size());

    server.enqueue(new MockResponse().setBody("{\"stored\":2}"));
    manager.flush();
    assertEquals(0, store.size());

    RecordedRequest retry = server.takeRequest();
    JsonArray readings =
        JsonParser.parseString(retry.getBody().readUtf8())
            .getAsJsonObject()
            .get("readings")
            .getAsJsonArray();
    assertEquals(1, readings.size());
  }

  @Test
  public void disabledTelemetrySendsNothing() {
    preferences.edit().putBoolean(ENABLED_KEY, false).apply();

    manager.onEnvReading(23.4f, 61.2f);
    manager.flush();

    assertEquals(1, store.size());
    assertEquals(0, server.getRequestCount());
  }

  @Test
  public void missingUrlSendsNothing() {
    preferences.edit().putString(URL_KEY, "").apply();

    manager.onEnvReading(23.4f, 61.2f);
    manager.flush();

    assertEquals(1, store.size());
    assertEquals(0, server.getRequestCount());
  }

  @Test
  public void batchSizeIsCappedAtServerLimit() throws InterruptedException {
    for (int i = 0; i < TelemetryClient.MAX_BATCH + 10; i++) {
      manager.onEnvReading(20f + i, 50f + i);
    }

    server.enqueue(new MockResponse().setBody("{\"stored\":100}"));
    manager.flush();

    assertEquals(10, store.size());
    RecordedRequest request = server.takeRequest();
    JsonArray readings =
        JsonParser.parseString(request.getBody().readUtf8())
            .getAsJsonObject()
            .get("readings")
            .getAsJsonArray();
    assertEquals(TelemetryClient.MAX_BATCH, readings.size());
  }
}