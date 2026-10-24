// OpenBot's WebRTC signaling messages, as its robot app sends and expects them.

export type RobotEvent =
  | { type: "offer"; sdp: string }
  | { type: "candidate"; candidate: RTCIceCandidateInit }
  | { type: "stop" };

export const joinMessage = (roomId: string) => JSON.stringify({ roomId, clientType: "browser" });

// Stopping and starting the robot's video server makes it send a new offer to whoever is in the room
export const RESTART_MESSAGES = [JSON.stringify({ command: "DISCONNECTED" }), JSON.stringify({ command: "CONNECTED" })];

export const answerMessage = (sdp: string) => JSON.stringify({ webrtc_event: { type: "answer", sdp } });

export const candidateMessage = ({ candidate, sdpMid, sdpMLineIndex }: RTCIceCandidateInit) =>
  JSON.stringify({ webrtc_event: { type: "candidate", id: sdpMid, label: sdpMLineIndex, candidate } });

export function parseRobotMessage(text: string): RobotEvent | undefined {
  try {
    const status = JSON.parse(text).status ?? {};
    if (status.VIDEO_COMMAND === "STOP") return { type: "stop" };
    if (!status.WEB_RTC_EVENT) return undefined;

    const event = JSON.parse(status.WEB_RTC_EVENT);
    if (event.type === "offer") return { type: "offer", sdp: event.sdp };
    if (event.type === "candidate") {
      return { type: "candidate", candidate: { candidate: event.candidate, sdpMid: event.id, sdpMLineIndex: event.label } };
    }
  } catch {
    // Not a message for us
  }
  return undefined;
}
