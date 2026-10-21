import { TIME_RANGES } from "../config";

export function renderRanges(container: HTMLElement, selected: number, onChange: (minutes: number) => void): void {
  const buttons = TIME_RANGES.map(({ label, minutes }) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    button.setAttribute("aria-pressed", String(minutes === selected));
    button.addEventListener("click", () => {
      buttons.forEach((other) => other.setAttribute("aria-pressed", String(other === button)));
      onChange(minutes);
    });
    return button;
  });
  container.replaceChildren(...buttons);
}
