import { Map as MlMap, Marker, NavigationControl, Popup, ScaleControl, setWorkerUrl, type CameraOptions, type GeoJSONSource } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url";
import type { Fix } from "../api";
import {
  BASEMAP_SOURCE,
  BASEMAP_STYLE_DARK,
  BASEMAP_STYLE_LIGHT,
  BUILDINGS_SOURCE_LAYER,
  CAMPUS_BOUNDS,
  CAMPUS_CENTER,
  DEFAULT_BUILDING_HEIGHT_M,
  MAP_MAX_ZOOM,
  MAP_MIN_ZOOM,
  MAP_ZOOM,
  START_IN_3D,
  VIEW_3D,
} from "../config";
import { formatCoord, formatDateTime } from "../format";
import { trailGeoJson } from "../geo";
import { cssVar, isDark, onThemeChange, reducedMotion } from "../theme";
import { createRobotElement } from "./robot";

// v6 ships its worker as a separate ES module; Vite bundles it and hands over the URL
setWorkerUrl(workerUrl);

const TRAIL = "optimus-trail";
const BUILDINGS = "optimus-buildings";

export interface RobotMap {
  update(fixes: Fix[]): void;
}

export function createRobotMap(container: HTMLElement, followButton: HTMLButtonElement, viewButton: HTMLButtonElement): RobotMap {
  const map = new MlMap({
    container,
    style: isDark() ? BASEMAP_STYLE_DARK : BASEMAP_STYLE_LIGHT,
    center: CAMPUS_CENTER,
    zoom: MAP_ZOOM,
    minZoom: MAP_MIN_ZOOM,
    maxZoom: MAP_MAX_ZOOM,
    maxBounds: CAMPUS_BOUNDS,
    maxPitch: 70,
    ...(START_IN_3D ? VIEW_3D : {}),
    attributionControl: { compact: true },
  });
  map.addControl(new NavigationControl({ visualizePitch: true }), "bottom-right");
  map.addControl(new ScaleControl({ unit: "metric" }), "bottom-right");

  let fixes: Fix[] = [];
  let is3d = START_IN_3D;
  let following = true;

  // A new basemap style drops our layers, so they are added on every style load
  // Trail first, then buildings on top: in 3D a building hides the trail behind it
  map.on("style.load", () => {
    const beforeLabels = map.getStyle().layers.find((layer) => layer.type === "symbol")?.id;
    map.addSource(TRAIL, { type: "geojson", data: trailGeoJson(fixes) });
    map.addLayer(
      {
        id: `${TRAIL}-casing`,
        type: "line",
        source: TRAIL,
        layout: { "line-cap": "round", "line-join": "round" },
        paint: { "line-color": cssVar("--trail-casing"), "line-width": 8 },
      },
      beforeLabels,
    );
    map.addLayer(
      {
        id: TRAIL,
        type: "line",
        source: TRAIL,
        layout: { "line-cap": "round", "line-join": "round" },
        paint: { "line-color": cssVar("--brand"), "line-width": 3.5 },
      },
      beforeLabels,
    );
    map.addLayer(
      {
        id: BUILDINGS,
        type: "fill-extrusion",
        source: BASEMAP_SOURCE,
        "source-layer": BUILDINGS_SOURCE_LAYER,
        minzoom: 14,
        layout: { visibility: is3d ? "visible" : "none" },
        paint: {
          "fill-extrusion-color": cssVar("--building"),
          "fill-extrusion-height": ["coalesce", ["get", "height"], DEFAULT_BUILDING_HEIGHT_M],
          "fill-extrusion-base": ["coalesce", ["get", "min_height"], 0],
        },
      },
      beforeLabels,
    );
  });
  onThemeChange(() => map.setStyle(isDark() ? BASEMAP_STYLE_DARK : BASEMAP_STYLE_LIGHT));

  const popup = new Popup({ offset: 30, closeButton: false, className: "robot-popup" });
  const robot = new Marker({ element: createRobotElement("robot-marker"), anchor: "center" }).setPopup(popup);

  const move = (options: CameraOptions) => (reducedMotion() ? map.jumpTo(options) : map.easeTo({ ...options, duration: 900 }));

  // Follow the robot until the user pans away; the button turns following back on
  map.on("dragstart", () => setFollowing(false));
  followButton.addEventListener("click", () => {
    setFollowing(true);
    const latest = fixes.at(-1);
    if (latest) move({ center: [latest.lon, latest.lat] });
  });
  function setFollowing(value: boolean) {
    following = value;
    followButton.setAttribute("aria-pressed", String(value));
  }
  setFollowing(true);

  // The button names the view it switches to
  const showViewButton = () => {
    viewButton.setAttribute("aria-pressed", String(is3d));
    viewButton.textContent = is3d ? "2D" : "3D";
  };
  showViewButton();
  viewButton.addEventListener("click", () => {
    is3d = !is3d;
    showViewButton();
    if (map.getLayer(BUILDINGS)) map.setLayoutProperty(BUILDINGS, "visibility", is3d ? "visible" : "none");
    move(is3d ? VIEW_3D : { pitch: 0, bearing: 0 });
  });

  return {
    update(next) {
      fixes = next;
      map.getSource<GeoJSONSource>(TRAIL)?.setData(trailGeoJson(fixes));
      const latest = fixes.at(-1);
      if (!latest) {
        robot.remove();
        return;
      }
      robot.setLngLat([latest.lon, latest.lat]).addTo(map);
      popup.setHTML(`<strong>Optimus</strong><span>${formatCoord(latest.lat)}, ${formatCoord(latest.lon)}</span><span>${formatDateTime(latest.t)}</span>`);
      if (following) move({ center: [latest.lon, latest.lat] });
    },
  };
}
