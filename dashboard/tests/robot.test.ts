import { describe, expect, it } from "vitest";
import { moodFor } from "../src/ui/robot";

describe("moodFor", () => {
  it("is awake while data is live", () => {
    expect(moodFor("live")).toBe("awake");
  });

  it("gets sleepy when data goes stale and sleeps when offline", () => {
    expect(moodFor("stale")).toBe("sleepy");
    expect(moodFor("offline")).toBe("asleep");
  });

  it("looks around while connecting", () => {
    expect(moodFor("connecting")).toBe("curious");
  });
});
