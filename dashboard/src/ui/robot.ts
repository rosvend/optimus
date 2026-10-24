// Optimus's face: the map marker, the masthead avatar and the favicon. Its eyes follow the data.
import type { StatusKind } from "./status";

export type Mood = "awake" | "curious" | "sleepy" | "asleep";

const MOODS: Record<StatusKind, Mood> = {
  live: "awake",
  connecting: "curious",
  stale: "sleepy",
  offline: "asleep",
};

export const moodFor = (status: StatusKind): Mood => MOODS[status];

export const ROBOT_SVG = `<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <circle cx="9" cy="37" r="6.5" fill="#2b3138"/><circle cx="9" cy="37" r="3" fill="#ff8a2a"/>
  <circle cx="55" cy="37" r="6.5" fill="#2b3138"/><circle cx="55" cy="37" r="3" fill="#ff8a2a"/>
  <rect x="10" y="9" width="44" height="48" rx="19" fill="#ff7a1a"/>
  <path d="M19 15a19 19 0 0 1 26 0" fill="none" stroke="#ffb27a" stroke-width="3" stroke-linecap="round" opacity=".8"/>
  <rect x="29" y="9.5" width="2.6" height="10" rx="1.3" fill="#ffd3ad"/>
  <rect x="33.4" y="9.5" width="2.6" height="10" rx="1.3" fill="#ffd3ad"/>
  <rect x="15.5" y="22" width="33" height="27" rx="12" fill="#14181d"/>
  <g class="robot-eyes" fill="#f2fbff">
    <circle class="robot-glow" cx="25" cy="34" r="7" fill="#9fdcff" opacity=".35"/>
    <circle class="robot-glow" cx="39" cy="34" r="7" fill="#9fdcff" opacity=".35"/>
    <circle cx="25" cy="34" r="4.4"/>
    <circle cx="39" cy="34" r="4.4"/>
  </g>
  <path class="robot-mouth" d="M29.5 42.2q2.5 2 5 0" fill="none" stroke="#f2fbff" stroke-width="1.6" stroke-linecap="round"/>
</svg>`;

export function createRobotElement(className: string): HTMLElement {
  const element = document.createElement("div");
  element.className = `robot ${className}`;
  element.dataset.mood = "curious";
  element.innerHTML = ROBOT_SVG;
  return element;
}

export function setMood(mood: Mood): void {
  document.querySelectorAll<HTMLElement>(".robot").forEach((robot) => (robot.dataset.mood = mood));
}

export function useRobotFavicon(): void {
  const link = document.createElement("link");
  link.rel = "icon";
  link.type = "image/svg+xml";
  link.href = `data:image/svg+xml,${encodeURIComponent(ROBOT_SVG)}`;
  document.head.append(link);
}
