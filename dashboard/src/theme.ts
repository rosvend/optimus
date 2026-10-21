export const cssVar = (name: string) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

export function onThemeChange(callback: () => void): void {
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", callback);
}
