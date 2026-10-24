import { describe, expect, it } from "vitest";
import { toFixes, toPoints } from "../src/api";

describe("toPoints", () => {
  it("returns readings oldest first with parsed times", () => {
    const points = toPoints([
      { ts: "2026-10-14T15:00:01.000Z", value: 23 },
      { ts: "2026-10-14T15:00:00.000Z", value: 22 },
    ]);

    expect(points).toEqual([
      { t: Date.parse("2026-10-14T15:00:00.000Z"), value: 22 },
      { t: Date.parse("2026-10-14T15:00:01.000Z"), value: 23 },
    ]);
  });

  it("skips items without a value", () => {
    expect(toPoints([{ ts: "2026-10-14T15:00:00.000Z" }])).toEqual([]);
  });
});

describe("toFixes", () => {
  it("keeps only items with both coordinates", () => {
    const fixes = toFixes([
      { ts: "2026-10-14T15:00:01.000Z", lat: 6.24, lon: -75.58 },
      { ts: "2026-10-14T15:00:00.000Z", lat: 6.24 },
    ]);

    expect(fixes).toEqual([{ t: Date.parse("2026-10-14T15:00:01.000Z"), lat: 6.24, lon: -75.58 }]);
  });
});
