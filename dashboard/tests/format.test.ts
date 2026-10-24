import { describe, expect, it } from "vitest";
import { formatAge, formatDistance } from "../src/format";

describe("formatAge", () => {
  it.each([
    [-500, "0 s ago"],
    [12_000, "12 s ago"],
    [5 * 60_000, "5 min ago"],
    [3 * 3_600_000, "3 h ago"],
    [72 * 3_600_000, "3 d ago"],
  ])("formats %i ms as %s", (ms, expected) => {
    expect(formatAge(ms)).toBe(expected);
  });
});

describe("formatDistance", () => {
  it("shows whole meters under a kilometer", () => {
    expect(formatDistance(0)).toBe("0 m");
    expect(formatDistance(412.6)).toBe("413 m");
  });

  it("switches to kilometers with two decimals", () => {
    expect(formatDistance(1234)).toBe("1.23 km");
  });
});
