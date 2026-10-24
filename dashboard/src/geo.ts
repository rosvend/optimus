import type { Feature, LineString } from "geojson";
import type { Fix } from "./api";

const EARTH_RADIUS_M = 6_371_000;

export function trailLengthM(fixes: Fix[]): number {
  let total = 0;
  for (let i = 1; i < fixes.length; i++) total += haversineM(fixes[i - 1], fixes[i]);
  return total;
}

export function trailGeoJson(fixes: Fix[]): Feature<LineString> {
  return {
    type: "Feature",
    properties: {},
    geometry: { type: "LineString", coordinates: fixes.map((fix) => [fix.lon, fix.lat]) },
  };
}

function haversineM(a: Fix, b: Fix): number {
  const rad = Math.PI / 180;
  const dLat = (b.lat - a.lat) * rad;
  const dLon = (b.lon - a.lon) * rad;
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(a.lat * rad) * Math.cos(b.lat * rad) * Math.sin(dLon / 2) ** 2;
  return 2 * EARTH_RADIUS_M * Math.asin(Math.sqrt(h));
}
