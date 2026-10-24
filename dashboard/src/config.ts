// Tunables for the dashboard. URLs are deployment-specific and loaded from /config.json at runtime.

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

// The robot never leaves the UPB Laureles campus, so the map is locked around it
export const CAMPUS_CENTER: [number, number] = [-75.59, 6.2418]; // lon, lat
// About 400 m of margin around the campus (OSM bbox 6.2398..6.2444, -75.5917..-75.5863)
export const CAMPUS_BOUNDS: [[number, number], [number, number]] = [
  [-75.5965, 6.2365],
  [-75.5815, 6.2477],
];
export const MAP_ZOOM = 17;
export const MAP_MIN_ZOOM = 15.5;
export const MAP_MAX_ZOOM = 20;

export const BASEMAP_STYLE_LIGHT = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json";
export const BASEMAP_STYLE_DARK = "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json";
export const BASEMAP_SOURCE = "protomaps";
export const BUILDINGS_SOURCE_LAYER = "buildings";
// Most campus buildings have no height in OpenStreetMap; assume three floors
export const DEFAULT_BUILDING_HEIGHT_M = 10;
export const VIEW_3D = { pitch: 58, bearing: -24 };
export const START_IN_3D = true;

// Robot camera over WebRTC; the signaling URL and room come from /config.json
export const SIGNALING_KEY_PARAM = "key";
export const VIDEO_ICE_SERVERS: RTCIceServer[] = [{ urls: "stun:stun.l.google.com:19302" }];
export const VIDEO_RECONNECT_MS = 5_000;
// Gives the phone time to release the camera between stopping and restarting its stream
export const VIDEO_RESTART_GAP_MS = 1_000;

export const API_KEY_STORAGE = "optimus.apiKey";
export const RUNTIME_CONFIG_PATH = "config.json";
