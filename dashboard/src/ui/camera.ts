import type { VideoState } from "../video";

const LABELS: Record<VideoState, string> = {
  connecting: "Connecting…",
  waiting: "Waiting for the robot",
  live: "Live",
  offline: "Video server unreachable",
};

export interface CameraPanel {
  showStream(stream: MediaStream | null): void;
  showState(state: VideoState): void;
}

export function createCameraPanel(panel: HTMLElement): CameraPanel {
  const video = panel.querySelector("video")!;
  const label = panel.querySelector<HTMLElement>(".camera-state")!;
  panel.hidden = false;

  return {
    showStream(stream) {
      video.srcObject = stream;
    },
    showState(state) {
      panel.dataset.state = state;
      label.textContent = LABELS[state];
    },
  };
}
