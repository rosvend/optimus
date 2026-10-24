package org.openbot.app.robot.env;

import android.content.Context;
import android.content.SharedPreferences;
import androidx.preference.PreferenceManager;

public class ControllerConfig {
  private static ControllerConfig _controllerConfig;
  SharedPreferences preferences;

  enum VIDEO_SERVER_TYPE {
    WEBRTC,
    RTSP
  }

  private String currentServerType;

  public static ControllerConfig getInstance() {
    if (_controllerConfig == null) {
      synchronized (PhoneController.class) {
        if (_controllerConfig == null) _controllerConfig = new ControllerConfig();
      }
    }

    return _controllerConfig;
  }

  void init(Context context) {
    preferences = PreferenceManager.getDefaultSharedPreferences(context);
    currentServerType = get("video_server", "WEBRTC");
  }

  private void set(String name, String value) {
    SharedPreferences.Editor editor = preferences.edit();
    editor.putString(name, value);
    editor.apply();
  }

  private String get(String name, String defaultValue) {
    try {
      return preferences.getString(name, defaultValue);
    } catch (ClassCastException e) {
      return defaultValue;
    }
  }

  private Boolean getBoolean(String name, Boolean defaultValue) {
    try {
      return preferences.getBoolean(name, defaultValue);
    } catch (ClassCastException e) {
      return defaultValue;
    }
  }

  private void setBoolean(String name, boolean value) {
    SharedPreferences.Editor editor = preferences.edit();
    editor.putBoolean(name, value);
    editor.apply();
  }

  public String getVideoServerType() {
    return get("video_server", "WEBRTC");
  }

  public void setVideoServerType(String type) {
    set("video_server", type);
  }

  /** Web signaling URL (machine running controller/web-server). Override in app settings. */
  public String getWebSignalingServerUrl() {
    // Default IP. Replace it with your own server IP address in Settings.
    return get("web_signaling_server", "ws://192.168.1.40:8080/ws");
  }

  public void setWebSignalingServerUrl(String url) {
    set("web_signaling_server", url);
  }

  /**
   * Room id that pairs the robot with a browser over the web signaling server. Generated once on
   * first use; the browser must join the same room. Shown in Settings under Web Controller.
   */
  public String getWebRoomId() {
    String roomId = get("web_room_id", "");
    if (roomId.trim().isEmpty()) {
      roomId = generateRoomId();
      set("web_room_id", roomId);
    }
    return roomId;
  }

  public static String generateRoomId() {
    // Unambiguous uppercase alphabet, easy to read and type on another device.
    String alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
    java.util.Random random = new java.util.Random();
    StringBuilder id = new StringBuilder(6);
    for (int i = 0; i < 6; i++) {
      id.append(alphabet.charAt(random.nextInt(alphabet.length())));
    }
    return id.toString();
  }
}