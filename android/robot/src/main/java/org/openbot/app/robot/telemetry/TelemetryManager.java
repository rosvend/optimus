package org.openbot.app.robot.telemetry;

import android.content.Context;
import android.content.SharedPreferences;
import androidx.preference.PreferenceManager;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import org.openbot.app.robot.BuildConfig;
import org.openbot.app.robot.vehicle.Vehicle;
import timber.log.Timber;

/**
 * Cloud telemetry: tags env readings from the robot with the phone GPS position, buffers them,
 * and periodically POSTs batches to the FIWARE telemetry microservice.
 *
 * <p>Readings stay buffered while the request fails (offline, bad key), and are retried on the
 * next flush; {@code age_ms} keeps their real capture time. The endpoint URL and API key are
 * configured in the app settings, defaulting to BuildConfig values from the gitignored
 * telemetry.properties.
 */
public final class TelemetryManager {
  private static final String PREF_ENABLED = "telemetry_enabled";
  private static final String PREF_URL = "telemetry_url";
  private static final String PREF_API_KEY = "telemetry_api_key";
  private static final long FLUSH_INTERVAL_MS = TimeUnit.SECONDS.toMillis(15);
  private static final int BUFFER_CAPACITY = 500;

  private static TelemetryManager instance;

  private final Context context;
  private final TelemetryStore store;
  private final TelemetryClient client;
  private final LiveLocation location;
  private ScheduledExecutorService executor;

  TelemetryManager(
      Context context, TelemetryStore store, TelemetryClient client, LiveLocation location) {
    this.context = context.getApplicationContext();
    this.store = store;
    this.client = client;
    this.location = location;
  }

  public static synchronized TelemetryManager getInstance(Context context) {
    if (instance == null) {
      instance =
          new TelemetryManager(
              context,
              new TelemetryStore(BUFFER_CAPACITY),
              new TelemetryClient(new okhttp3.OkHttpClient()),
              new LiveLocation());
    }
    return instance;
  }

  /** Wires the vehicle env listener and starts the periodic upload loop. Idempotent. */
  public synchronized void start(Vehicle vehicle) {
    if (executor != null) {
      return;
    }
    vehicle.setEnvListener(this::onEnvReading);
    executor = Executors.newSingleThreadScheduledExecutor();
    executor.scheduleWithFixedDelay(
        this::safeFlush, FLUSH_INTERVAL_MS, FLUSH_INTERVAL_MS, TimeUnit.MILLISECONDS);
  }

  void onEnvReading(float temperature, float humidity) {
    double[] fix = location.current();
    store.add(
        new TelemetryReading(
            System.currentTimeMillis(),
            temperature,
            humidity,
            fix == null ? null : fix[0],
            fix == null ? null : fix[1]));
  }

  private void safeFlush() {
    try {
      flush();
    } catch (Exception e) {
      Timber.e(e, "Telemetry flush failed");
    }
  }

  void flush() {
    Config config = readConfig();
    if (!config.enabled) {
      return;
    }
    location.ensureStarted(context);
    List<TelemetryReading> batch = store.peek(TelemetryClient.MAX_BATCH);
    if (batch.isEmpty()) {
      return;
    }
    if (client.upload(config.url, config.apiKey, batch, System.currentTimeMillis())) {
      store.removeFirst(batch.size());
      Timber.i("Uploaded %d telemetry readings, %d still buffered", batch.size(), store.size());
    } else {
      Timber.w("Telemetry upload failed, keeping %d readings buffered", store.size());
    }
  }

  private Config readConfig() {
    SharedPreferences preferences = PreferenceManager.getDefaultSharedPreferences(context);
    boolean enabled = preferences.getBoolean(PREF_ENABLED, true);
    String url = preferences.getString(PREF_URL, BuildConfig.TELEMETRY_URL);
    String apiKey = preferences.getString(PREF_API_KEY, BuildConfig.TELEMETRY_API_KEY);
    return new Config(enabled && !isBlank(url) && !isBlank(apiKey), url, apiKey);
  }

  private static boolean isBlank(String value) {
    return value == null || value.trim().isEmpty();
  }

  private static final class Config {
    final boolean enabled;
    final String url;
    final String apiKey;

    Config(boolean enabled, String url, String apiKey) {
      this.enabled = enabled;
      this.url = url;
      this.apiKey = apiKey;
    }
  }
}