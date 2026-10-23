package org.openbot.app.robot.telemetry;

import java.io.IOException;
import java.util.List;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;
import timber.log.Timber;

/** POSTs a batch of readings to the telemetry API with the {@code x-api-key} header. */
public final class TelemetryClient {
  /** The API rejects requests with more than 50 readings. */
  public static final int MAX_BATCH = 50;

  private static final MediaType JSON = MediaType.get("application/json; charset=utf-8");

  private final OkHttpClient httpClient;

  public TelemetryClient(OkHttpClient httpClient) {
    this.httpClient = httpClient;
  }

  /** Returns true when the server stored the batch; on failure the caller keeps the readings. */
  public boolean upload(String url, String apiKey, List<TelemetryReading> readings, long nowMs) {
    String body = TelemetryJson.build(TelemetryJson.DEFAULT_DEVICE, readings, nowMs);
    Request request =
        new Request.Builder()
            .url(url)
            .header("x-api-key", apiKey)
            .post(RequestBody.create(body, JSON))
            .build();
    try (Response response = httpClient.newCall(request).execute()) {
      if (!response.isSuccessful()) {
        Timber.w("Telemetry upload failed with HTTP %d", response.code());
        return false;
      }
      return true;
    } catch (IOException e) {
      Timber.e(e, "Telemetry upload failed");
      return false;
    }
  }
}