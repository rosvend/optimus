import L from "leaflet";
import "leaflet/dist/leaflet.css";
import type { Fix } from "../api";
import { MAP_ATTRIBUTION, MAP_DEFAULT_CENTER, MAP_DEFAULT_ZOOM, MAP_FOLLOW_ZOOM, MAP_TILE_URL } from "../config";
import { formatCoord, formatDateTime } from "../format";
import { cssVar, onThemeChange } from "../theme";

export interface RobotMap {
  update(fixes: Fix[]): void;
}

export function createRobotMap(container: HTMLElement, followButton: HTMLButtonElement): RobotMap {
  const empty = container.parentElement!.querySelector<HTMLElement>(".empty")!;
  const map = L.map(container).setView(MAP_DEFAULT_CENTER, MAP_DEFAULT_ZOOM);
  L.tileLayer(MAP_TILE_URL, { attribution: MAP_ATTRIBUTION, maxZoom: 19 }).addTo(map);

  const trail = L.polyline([], { weight: 3, opacity: 0.8 }).addTo(map);
  const robot = L.circleMarker(MAP_DEFAULT_CENTER, { radius: 8, weight: 2, fillOpacity: 1 }).bindTooltip("");
  const applyTheme = () => {
    trail.setStyle({ color: cssVar("--series-1") });
    robot.setStyle({ color: cssVar("--surface"), fillColor: cssVar("--series-1") });
  };
  applyTheme();
  onThemeChange(applyTheme);

  // Follow the robot until the user pans away; the button turns following back on
  let following = true;
  let zoomedIn = false;
  map.on("dragstart", () => setFollowing(false));
  followButton.addEventListener("click", () => {
    setFollowing(true);
    if (map.hasLayer(robot)) map.setView(robot.getLatLng(), MAP_FOLLOW_ZOOM);
  });
  function setFollowing(value: boolean) {
    following = value;
    followButton.disabled = value;
    followButton.textContent = value ? "Following robot" : "Follow robot";
  }
  setFollowing(true);

  return {
    update(fixes) {
      empty.hidden = fixes.length > 0;
      trail.setLatLngs(fixes.map((fix) => [fix.lat, fix.lon]));
      const latest = fixes.at(-1);
      if (!latest) {
        robot.remove();
        return;
      }
      robot
        .setLatLng([latest.lat, latest.lon])
        .setTooltipContent(`${formatCoord(latest.lat)}, ${formatCoord(latest.lon)}<br>${formatDateTime(latest.t)}`)
        .addTo(map);
      if (following) map.setView([latest.lat, latest.lon], zoomedIn ? map.getZoom() : MAP_FOLLOW_ZOOM);
      zoomedIn = true;
    },
  };
}
