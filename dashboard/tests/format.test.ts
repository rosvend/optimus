import { describe, expect, it } from "vitest";
import { formatAge } from "../src/format";

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
