// Tunables for the dashboard. The API URL is deployment-specific and loaded from /config.json at runtime.

export const POLL_INTERVAL_MS = 5_000;
export const STALE_AFTER_MS = 60_000;
export const QUERY_LIMIT = 500;

export const TIME_RANGES = [
  { label: "15 min", minutes: 15 },
  { label: "1 h", minutes: 60 },
  { label: "6 h", minutes: 360 },
  { label: "24 h", minutes: 1440 },
] as const;
export const DEFAULT_RANGE_MINUTES = 60;

export const MAP_TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png";
export const MAP_ATTRIBUTION = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';
export const MAP_DEFAULT_CENTER: [number, number] = [6.2442, -75.5812];
export const MAP_DEFAULT_ZOOM = 13;
export const MAP_FOLLOW_ZOOM = 17;

export const API_KEY_STORAGE = "optimus.apiKey";
export const RUNTIME_CONFIG_PATH = "config.json";
