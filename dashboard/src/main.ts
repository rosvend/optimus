import { fetchTelemetry, loadRuntimeConfig, UnauthorizedError, type RuntimeConfig, type Telemetry } from "./api";
import { API_KEY_STORAGE, DEFAULT_RANGE_MINUTES, POLL_INTERVAL_MS, STALE_AFTER_MS } from "./config";
import { formatAge } from "./format";
import { createCameraPanel } from "./ui/camera";
import { createLineChart } from "./ui/lineChart";
import { askForApiKey } from "./ui/login";
import { createRobotMap } from "./ui/map";
import { renderRanges } from "./ui/ranges";
import { createRobotElement, moodFor, setMood, useRobotFavicon } from "./ui/robot";
import { setStatus as setStatusLabel, type StatusKind } from "./ui/status";
import { latestTimestamp, renderTiles } from "./ui/tiles";
import { watchRobotCamera } from "./video";

useRobotFavicon();
document.querySelector("#avatar")!.append(createRobotElement("robot-avatar"));
document.querySelector("#login-avatar")!.append(createRobotElement("robot-avatar"));

const temperatureChart = createLineChart(document.querySelector("#chart-temperature")!, "°C", "temperature");
const humidityChart = createLineChart(document.querySelector("#chart-humidity")!, "%", "humidity");
const robotMap = createRobotMap(document.querySelector("#map")!, document.querySelector("#follow")!, document.querySelector("#view")!);

let rangeMinutes = DEFAULT_RANGE_MINUTES;
let apiUrl = "";
let apiKey = readStoredKey();
let requestId = 0;
let timer: number | undefined;

renderRanges(document.querySelector("#ranges")!, rangeMinutes, (minutes) => {
  rangeMinutes = minutes;
  refresh();
});

async function start(): Promise<void> {
  let config: RuntimeConfig;
  try {
    config = await loadRuntimeConfig();
  } catch {
    setStatus("offline", "Missing config.json");
    return;
  }
  apiUrl = config.apiUrl;
  if (!apiKey) await login();
  refresh();
  if (config.signalingUrl && config.roomId) startCamera(config.signalingUrl, config.roomId);
}

function startCamera(url: string, roomId: string): void {
  const camera = createCameraPanel(document.querySelector("#camera")!);
  watchRobotCamera({ url, roomId, apiKey: () => apiKey, onStream: camera.showStream, onState: camera.showState });
}

async function refresh(): Promise<void> {
  window.clearTimeout(timer);
  const id = ++requestId;
  const to = Date.now();
  const from = to - rangeMinutes * 60_000;
  try {
    const data = await fetchTelemetry(apiUrl, apiKey, new Date(from));
    if (id !== requestId) return;
    render(data, from, to);
  } catch (error) {
    if (id !== requestId) return;
    if (error instanceof UnauthorizedError) {
      await login("That API key was rejected. Try again.");
      return refresh();
    } else {
      setStatus("offline", "Can't reach the API");
    }
  }
  timer = window.setTimeout(refresh, POLL_INTERVAL_MS);
}

function render(data: Telemetry, from: number, to: number): void {
  temperatureChart.update(data.temperature, from, to);
  humidityChart.update(data.humidity, from, to);
  robotMap.update(data.gps);
  renderTiles(data, to);

  const last = latestTimestamp(data);
  if (last === undefined) setStatus("stale", "No data in range");
  else if (to - last > STALE_AFTER_MS) setStatus("stale", `Stale · ${formatAge(to - last)}`);
  else setStatus("live", "Live");
}

function setStatus(kind: StatusKind, text: string): void {
  setStatusLabel(kind, text);
  setMood(moodFor(kind));
}

async function login(message?: string): Promise<void> {
  apiKey = await askForApiKey(message);
  try {
    localStorage.setItem(API_KEY_STORAGE, apiKey);
  } catch {
    // Private mode: the key just won't survive a reload
  }
}

function readStoredKey(): string {
  try {
    return localStorage.getItem(API_KEY_STORAGE) ?? "";
  } catch {
    return "";
  }
}

start();
