import { describe, expect, it } from "vitest";
import { roundTimeTicks } from "../src/ui/lineChart";

const MINUTE = 60_000;

describe("roundTimeTicks", () => {
  it("places ticks on round 15 minute marks for a one hour window", () => {
    const from = 7 * MINUTE;
    const ticks = roundTimeTicks(from, from + 60 * MINUTE);

    expect(ticks).toEqual([15, 30, 45, 60].map((m) => m * MINUTE));
  });

  it("never returns more than five ticks", () => {
    expect(roundTimeTicks(0, 1440 * MINUTE).length).toBeLessThanOrEqual(5);
  });
});
