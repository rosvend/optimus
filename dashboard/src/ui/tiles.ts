import type { Telemetry } from "../api";
import { formatAge, formatCoord, formatDateTime, formatNumber, formatTime } from "../format";

const byId = (id: string) => document.getElementById(id)!;

export function renderTiles(data: Telemetry, now: number): void {
  const temperature = data.temperature.at(-1);
  const humidity = data.humidity.at(-1);
  const fix = data.gps.at(-1);
  const last = latestTimestamp(data);

  setTile("tile-temperature", temperature && formatNumber(temperature.value), temperature && `at ${formatTime(temperature.t)}`);
  setTile("tile-humidity", humidity && formatNumber(humidity.value), humidity && `at ${formatTime(humidity.t)}`);
  setTile("tile-position", fix && `${formatCoord(fix.lat)}, ${formatCoord(fix.lon)}`, fix && `at ${formatTime(fix.t)}`);
  const hasLast = last !== undefined;
  setTile("tile-last", hasLast ? formatAge(now - last) : undefined, hasLast ? formatDateTime(last) : undefined);
}

export function latestTimestamp(data: Telemetry): number | undefined {
  const times = [data.temperature.at(-1)?.t, data.humidity.at(-1)?.t, data.gps.at(-1)?.t].filter((t) => t !== undefined);
  return times.length ? Math.max(...times) : undefined;
}

function setTile(id: string, value: string | undefined, meta: string | undefined): void {
  byId(id).textContent = value ?? "–";
  byId(`${id}-meta`).textContent = meta ?? "No data in this time range";
}
