import { describe, expect, it } from "vitest";
import { trailGeoJson, trailLengthM } from "../src/geo";

const fix = (t: number, lat: number, lon: number) => ({ t, lat, lon });

describe("trailLengthM", () => {
  it("is zero without at least two fixes", () => {
    expect(trailLengthM([])).toBe(0);
    expect(trailLengthM([fix(0, 6.24, -75.59)])).toBe(0);
  });

  it("sums the great-circle distance between consecutive fixes", () => {
    // 0.001° of latitude is about 111 m anywhere
    const fixes = [fix(0, 6.24, -75.59), fix(1, 6.241, -75.59), fix(2, 6.242, -75.59)];

    expect(trailLengthM(fixes)).toBeCloseTo(222.4, 0);
  });
});

describe("trailGeoJson", () => {
  it("builds a line in lon, lat order", () => {
    const line = trailGeoJson([fix(0, 6.24, -75.59), fix(1, 6.241, -75.589)]);

    expect(line.geometry).toEqual({ type: "LineString", coordinates: [[-75.59, 6.24], [-75.589, 6.241]] });
  });
});
