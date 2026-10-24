const darkQuery = () => window.matchMedia("(prefers-color-scheme: dark)");

export const cssVar = (name: string) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
export const isDark = () => darkQuery().matches;
export const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

export function onThemeChange(callback: () => void): void {
  darkQuery().addEventListener("change", callback);
}
