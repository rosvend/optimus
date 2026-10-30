import { describe, expect, it } from "vitest";
import { answerMessage, candidateMessage, joinMessage, parseRobotMessage, RESTART_MESSAGES } from "../src/signaling";

describe("browser messages", () => {
  it("joins a room as the browser", () => {
    expect(JSON.parse(joinMessage("OPTIMUS"))).toEqual({ roomId: "OPTIMUS", clientType: "browser" });
  });

  it("restarts the robot's stream so it sends a fresh offer", () => {
    expect(RESTART_MESSAGES.map((m) => JSON.parse(m))).toEqual([{ command: "DISCONNECTED" }, { command: "CONNECTED" }]);
  });

  it("wraps the answer and candidates as OpenBot webrtc_events", () => {
    expect(JSON.parse(answerMessage("v=0"))).toEqual({ webrtc_event: { type: "answer", sdp: "v=0" } });
    expect(JSON.parse(candidateMessage({ candidate: "candidate:1", sdpMid: "0", sdpMLineIndex: 0 }))).toEqual({
      webrtc_event: { type: "candidate", id: "0", label: 0, candidate: "candidate:1" },
    });
  });
});

describe("parseRobotMessage", () => {
  const status = (name: string, value: string) => JSON.stringify({ status: { [name]: value }, roomId: "OPTIMUS" });

  it("reads an offer sent as a JSON string inside WEB_RTC_EVENT", () => {
    expect(parseRobotMessage(status("WEB_RTC_EVENT", JSON.stringify({ type: "offer", sdp: "v=0" })))).toEqual({ type: "offer", sdp: "v=0" });
  });

  it("reads ICE candidates in browser form", () => {
    const event = JSON.stringify({ type: "candidate", id: "0", label: 0, candidate: "candidate:1" });

    expect(parseRobotMessage(status("WEB_RTC_EVENT", event))).toEqual({
      type: "candidate",
      candidate: { candidate: "candidate:1", sdpMid: "0", sdpMLineIndex: 0 },
    });
  });

  it("reads the stop command", () => {
    expect(parseRobotMessage(status("VIDEO_COMMAND", "STOP"))).toEqual({ type: "stop" });
  });

  it("ignores everything else", () => {
    expect(parseRobotMessage(status("VIDEO_COMMAND", "START"))).toBeUndefined();
    expect(parseRobotMessage(status("SPEED_MODE", "SLOW"))).toBeUndefined();
    expect(parseRobotMessage("not json")).toBeUndefined();
  });
});
