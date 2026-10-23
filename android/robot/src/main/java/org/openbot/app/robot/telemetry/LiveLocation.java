package org.openbot.app.robot.telemetry;

import android.Manifest;
import android.content.Context;
import android.content.pm.PackageManager;
import android.location.Location;
import androidx.annotation.Nullable;
import androidx.core.content.ContextCompat;
import com.google.android.gms.location.FusedLocationProviderClient;
import com.google.android.gms.location.LocationCallback;
import com.google.android.gms.location.LocationRequest;
import com.google.android.gms.location.LocationResult;
import com.google.android.gms.location.LocationServices;
import java.util.concurrent.TimeUnit;

/**
 * Keeps the last phone GPS fix in memory so every buffered reading can be tagged with the
 * position where it was taken. Fixes older than {@link #STALE_AFTER_MS} are not attached.
 */
final class LiveLocation {
  private static final long UPDATE_INTERVAL_MS = TimeUnit.SECONDS.toMillis(10);
  private static final long STALE_AFTER_MS = TimeUnit.MINUTES.toMillis(5);

  private final LocationCallback callback =
      new LocationCallback() {
        @Override
        public void onLocationResult(LocationResult result) {
          Location location = result.getLastLocation();
          if (location != null) {
            lat = location.getLatitude();
            lon = location.getLongitude();
            fixTimeMs = location.getTime();
            hasFix = true;
          }
        }
      };

  private FusedLocationProviderClient client;
  private volatile double lat;
  private volatile double lon;
  private volatile long fixTimeMs;
  private volatile boolean hasFix = false;
  private boolean tracking = false;

  /**
   * Starts location updates if permission is granted; safe to call again after the user grants
   * location access or enables telemetry.
   */
  synchronized void ensureStarted(Context context) {
    if (tracking) {
      return;
    }
    if (!hasLocationPermission(context)) {
      return;
    }
    if (client == null) {
      client = LocationServices.getFusedLocationProviderClient(context);
    }
    try {
      client.requestLocationUpdates(getLocationRequest(), callback, context.getMainLooper());
      tracking = true;
    } catch (SecurityException e) {
      tracking = false;
    }
  }

  synchronized void stop() {
    if (tracking && client != null) {
      client.removeLocationUpdates(callback);
    }
    tracking = false;
  }

  /** Last fix as {@code [lat, lon]}, or null while there is no fresh fix. */
  @Nullable
  double[] current() {
    if (!hasFix || System.currentTimeMillis() - fixTimeMs > STALE_AFTER_MS) {
      return null;
    }
    return new double[] {lat, lon};
  }

  synchronized boolean isTracking() {
    return tracking;
  }

  private static boolean hasLocationPermission(Context context) {
    return ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION)
            == PackageManager.PERMISSION_GRANTED
        || ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_COARSE_LOCATION)
            == PackageManager.PERMISSION_GRANTED;
  }

  private static LocationRequest getLocationRequest() {
    LocationRequest request = new LocationRequest();
    request.setInterval(UPDATE_INTERVAL_MS);
    request.setPriority(LocationRequest.PRIORITY_HIGH_ACCURACY);
    return request;
  }
}