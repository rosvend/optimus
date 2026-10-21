export type StatusKind = "connecting" | "live" | "stale" | "offline";

const status = document.querySelector<HTMLElement>("#status")!;
const label = status.querySelector<HTMLElement>(".status-label")!;

export function setStatus(kind: StatusKind, text: string): void {
  status.dataset.kind = kind;
  label.textContent = text;
}
