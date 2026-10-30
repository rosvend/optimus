package org.openbot.app.robot.env;

import android.content.Context;
import android.graphics.Bitmap;
import java.nio.ByteBuffer;
import org.webrtc.CapturerObserver;
import org.webrtc.JavaI420Buffer;
import org.webrtc.SurfaceTextureHelper;
import org.webrtc.VideoCapturer;
import org.webrtc.VideoFrame;
import org.webrtc.YuvHelper;

/**
 * Optimus: streams the frames of a screen that already has the camera open (CameraX in
 * CameraFragment, e.g. person following) instead of opening it a second time. Android lets only
 * one client use a camera, so WebRTC's own Camera2Capturer took it away from the detector.
 *
 * <p>The screen marks the camera as owned while it is bound and pushes frames with {@link
 * #deliver}; WebRtcServer picks this capturer whenever the camera is owned, and restarts the
 * stream when ownership changes.
 */
public class SharedCameraCapturer implements VideoCapturer {

  public interface OwnershipListener {
    void onCameraOwnershipChanged(boolean owned);
  }

  private static volatile boolean cameraOwned = false;
  private static volatile SharedCameraCapturer capturing;
  private static OwnershipListener ownershipListener;

  private CapturerObserver observer;
  private ByteBuffer rgba;

  /** Called on the main thread when a camera screen binds (true) or releases (false) the camera. */
  public static void setCameraOwned(boolean owned) {
    if (cameraOwned == owned) return;
    cameraOwned = owned;
    if (ownershipListener != null) ownershipListener.onCameraOwnershipChanged(owned);
  }

  public static boolean isCameraOwned() {
    return cameraOwned;
  }

  public static void setOwnershipListener(OwnershipListener listener) {
    ownershipListener = listener;
  }

  /** True while a stream is consuming frames, so screens can skip the work otherwise. */
  public static boolean isCapturing() {
    return capturing != null;
  }

  /** Sends an upright frame to the stream. Width and height should be even. */
  public static void deliver(Bitmap frame) {
    SharedCameraCapturer capturer = capturing;
    if (capturer != null) capturer.send(frame);
  }

  private synchronized void send(Bitmap frame) {
    if (observer == null) return;
    int width = frame.getWidth();
    int height = frame.getHeight();
    int size = width * height * 4;
    if (rgba == null || rgba.capacity() != size) rgba = ByteBuffer.allocateDirect(size);
    rgba.rewind();
    frame.copyPixelsToBuffer(rgba);
    rgba.rewind();

    // ARGB_8888 bitmaps are R,G,B,A in memory, which libyuv calls ABGR
    JavaI420Buffer i420 = JavaI420Buffer.allocate(width, height);
    YuvHelper.ABGRToI420(
        rgba,
        width * 4,
        i420.getDataY(),
        i420.getStrideY(),
        i420.getDataU(),
        i420.getStrideU(),
        i420.getDataV(),
        i420.getStrideV(),
        width,
        height);
    VideoFrame videoFrame = new VideoFrame(i420, 0, System.nanoTime());
    observer.onFrameCaptured(videoFrame);
    videoFrame.release();
  }

  @Override
  public synchronized void initialize(
      SurfaceTextureHelper helper, Context context, CapturerObserver capturerObserver) {
    observer = capturerObserver;
  }

  @Override
  public void startCapture(int width, int height, int fps) {
    capturing = this;
    if (observer != null) observer.onCapturerStarted(true);
  }

  @Override
  public void stopCapture() {
    if (capturing == this) capturing = null;
    synchronized (this) {
      if (observer != null) observer.onCapturerStopped();
    }
  }

  @Override
  public void changeCaptureFormat(int width, int height, int fps) {}

  @Override
  public synchronized void dispose() {
    if (capturing == this) capturing = null;
    observer = null;
  }

  @Override
  public boolean isScreencast() {
    return false;
  }
}
