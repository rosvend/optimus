import { QUERY_LIMIT, RUNTIME_CONFIG_PATH } from "./config";

export interface Point {
  t: number;
  value: number;
}

export interface Fix {
  t: number;
  lat: number;
  lon: number;
}

export interface Telemetry {
  temperature: Point[];
  humidity: Point[];
  gps: Fix[];
}

interface RawItem {
  ts: string;
  value?: number;
  lat?: number;
  lon?: number;
}

export class UnauthorizedError extends Error {}

export interface RuntimeConfig {
  apiUrl: string;
  signalingUrl?: string;
  roomId?: string;
}

export async function loadRuntimeConfig(): Promise<RuntimeConfig> {
  const response = await fetch(RUNTIME_CONFIG_PATH);
  if (!response.ok) throw new Error(`missing ${RUNTIME_CONFIG_PATH}`);
  return response.json();
}

export async function fetchTelemetry(apiUrl: string, apiKey: string, since: Date): Promise<Telemetry> {
  const get = (sensor: string) => fetchSensor(apiUrl, apiKey, sensor, since);
  const [temperature, humidity, gps] = await Promise.all([get("temperature"), get("humidity"), get("gps")]);
  return {
    temperature: toPoints(temperature),
    humidity: toPoints(humidity),
    gps: toFixes(gps),
  };
}

async function fetchSensor(apiUrl: string, apiKey: string, sensor: string, since: Date): Promise<RawItem[]> {
  // Relative when the FIWARE microservice serves the dashboard itself
  const url = new URL(apiUrl, window.location.href);
  url.search = new URLSearchParams({ sensor, from: since.toISOString(), limit: String(QUERY_LIMIT) }).toString();
  const response = await fetch(url, { headers: { "x-api-key": apiKey } });
  if (response.status === 401) throw new UnauthorizedError("invalid API key");
  if (!response.ok) throw new Error(`${sensor}: HTTP ${response.status}`);
  return (await response.json()).items;
}

// The API returns newest first; charts and the trail want oldest first
export function toPoints(items: RawItem[]): Point[] {
  return items
    .filter((item) => typeof item.value === "number")
    .map((item) => ({ t: Date.parse(item.ts), value: item.value! }))
    .reverse();
}

export function toFixes(items: RawItem[]): Fix[] {
  return items
    .filter((item) => typeof item.lat === "number" && typeof item.lon === "number")
    .map((item) => ({ t: Date.parse(item.ts), lat: item.lat!, lon: item.lon! }))
    .reverse();
}
