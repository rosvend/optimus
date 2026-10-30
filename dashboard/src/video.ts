// Watches the robot's camera: joins the signaling room, answers the robot's WebRTC offer and
// hands over the stream. Reconnects whenever the signaling socket drops.
import { SIGNALING_KEY_PARAM, VIDEO_ICE_SERVERS, VIDEO_RECONNECT_MS, VIDEO_RESTART_GAP_MS } from "./config";
import { answerMessage, candidateMessage, joinMessage, parseRobotMessage, RESTART_MESSAGES, type RobotEvent } from "./signaling";

export type VideoState = "connecting" | "waiting" | "live" | "offline";

export interface VideoOptions {
  url: string;
  roomId: string;
  apiKey: () => string;
  onStream: (stream: MediaStream | null) => void;
  onState: (state: VideoState) => void;
}

export function watchRobotCamera({ url, roomId, apiKey, onStream, onState }: VideoOptions): void {
  let peer: RTCPeerConnection | undefined;
  let queue = Promise.resolve();

  connect();

  function connect() {
    onState("connecting");
    const socketUrl = new URL(url);
    socketUrl.searchParams.set(SIGNALING_KEY_PARAM, apiKey());
    const socket = new WebSocket(socketUrl);
    const send = (message: string) => socket.readyState === WebSocket.OPEN && socket.send(message);

    socket.onopen = () => {
      onState("waiting");
      send(joinMessage(roomId));
      send(RESTART_MESSAGES[0]);
      window.setTimeout(() => send(RESTART_MESSAGES[1]), VIDEO_RESTART_GAP_MS);
    };
    socket.onmessage = ({ data }) => {
      const event = parseRobotMessage(data);
      // One step at a time: candidates can't be added before the offer is applied
      if (event) queue = queue.then(() => handle(event, send)).catch((error) => console.warn("video:", error));
    };
    socket.onclose = () => {
      stop();
      onState("offline");
      window.setTimeout(connect, VIDEO_RECONNECT_MS);
    };
  }

  async function handle(event: RobotEvent, send: (message: string) => void) {
    if (event.type === "candidate") return peer?.addIceCandidate(event.candidate);
    stop();
    onState("waiting");
    if (event.type === "stop") return;

    peer = new RTCPeerConnection({ iceServers: VIDEO_ICE_SERVERS });
    peer.ontrack = ({ streams, track }) => {
      onStream(streams[0] ?? new MediaStream([track]));
      onState("live");
    };
    peer.onicecandidate = ({ candidate }) => candidate && send(candidateMessage(candidate.toJSON()));
    await peer.setRemoteDescription({ type: "offer", sdp: event.sdp });
    await peer.setLocalDescription(await peer.createAnswer());
    send(answerMessage(peer.localDescription!.sdp));
  }

  function stop() {
    peer?.close();
    peer = undefined;
    onStream(null);
  }
}
