import { Chart, Filler, LinearScale, LineController, LineElement, PointElement, Tooltip, type Plugin } from "chart.js";
import type { Point } from "../api";
import { formatDateTime, formatNumber, formatTime } from "../format";
import { cssVar, onThemeChange } from "../theme";

const TICK_STEPS_MIN = [1, 2, 5, 10, 15, 30, 60, 120, 180, 240, 360, 720, 1440];
const MAX_TIME_TICKS = 5;

Chart.register(LineController, LineElement, PointElement, LinearScale, Tooltip, Filler);

export interface LineChart {
  update(points: Point[], from: number, to: number): void;
}

// Vertical hairline at the hovered X so readers aim at a time, not at the line
const crosshair: Plugin<"line"> = {
  id: "crosshair",
  afterDatasetsDraw(chart) {
    const active = chart.tooltip?.getActiveElements()[0];
    if (!active) return;
    const { ctx, chartArea } = chart;
    ctx.save();
    ctx.strokeStyle = cssVar("--axis");
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(active.element.x, chartArea.top);
    ctx.lineTo(active.element.x, chartArea.bottom);
    ctx.stroke();
    ctx.restore();
  },
};

export function createLineChart(canvas: HTMLCanvasElement, unit: string, color: string): LineChart {
  const empty = canvas.parentElement!.querySelector<HTMLElement>(".empty")!;
  const chart = new Chart(canvas, {
    type: "line",
    data: { datasets: [{ data: [] as { x: number; y: number }[], parsing: false }] },
    plugins: [crosshair],
    options: {
      animation: false,
      layout: { padding: { right: 8 } },
      maintainAspectRatio: false,
      interaction: { mode: "nearest", axis: "x", intersect: false },
      elements: {
        line: { borderWidth: 2, borderCapStyle: "round", borderJoinStyle: "round", tension: 0.25, fill: "origin" },
        point: { radius: (ctx) => (ctx.dataIndex === ctx.dataset.data.length - 1 ? 4 : 0), hoverRadius: 5, borderWidth: 2, hitRadius: 12 },
      },
      scales: {
        x: {
          type: "linear",
          afterBuildTicks: (axis) => {
            axis.ticks = roundTimeTicks(axis.min, axis.max).map((value) => ({ value }));
          },
          ticks: { callback: (value) => formatTime(Number(value)), font: { family: "Barlow Semi Condensed", size: 11 } },
          grid: { display: false },
        },
        y: { grace: "10%", ticks: { maxTicksLimit: 4, callback: (value) => `${value}`, font: { family: "Barlow Semi Condensed", size: 11 } }, border: { display: false } },
      },
      plugins: {
        tooltip: {
          displayColors: false,
          callbacks: {
            title: (items) => formatDateTime(items[0].parsed.x!),
            label: (item) => `${formatNumber(item.parsed.y!)} ${unit}`,
          },
        },
      },
    },
  });

  applyTheme(chart, color);
  onThemeChange(() => {
    applyTheme(chart, color);
    chart.update();
  });

  return {
    update(points, from, to) {
      chart.data.datasets[0].data = points.map((p) => ({ x: p.t, y: p.value }));
      chart.options.scales!.x!.min = from;
      chart.options.scales!.x!.max = to;
      chart.update();
      empty.hidden = points.length > 0;
    },
  };
}

// Ticks on round minutes (e.g. every 15 min for 1 h) instead of arbitrary milliseconds
export function roundTimeTicks(from: number, to: number): number[] {
  const step = TICK_STEPS_MIN.find((minutes) => (to - from) / (minutes * 60_000) <= MAX_TIME_TICKS)! * 60_000;
  const ticks = [];
  for (let t = Math.ceil(from / step) * step; t <= to; t += step) ticks.push(t);
  return ticks;
}

// `color` names a CSS variable pair: --<color> for the line and --<color>-wash for the fill
function applyTheme(chart: Chart<"line">, color: string): void {
  const dataset = chart.data.datasets[0];
  dataset.borderColor = cssVar(`--${color}`);
  dataset.backgroundColor = cssVar(`--${color}-wash`);
  dataset.pointBackgroundColor = cssVar(`--${color}`);
  dataset.pointBorderColor = cssVar("--surface");

  const { x, y } = chart.options.scales!;
  x!.ticks!.color = cssVar("--ink-3");
  x!.border = { color: cssVar("--axis") };
  y!.ticks!.color = cssVar("--ink-3");
  y!.grid = { color: cssVar("--grid") };

  const tooltip = chart.options.plugins!.tooltip!;
  tooltip.backgroundColor = cssVar("--ink");
  tooltip.titleColor = cssVar("--surface");
  tooltip.bodyColor = cssVar("--surface");
}
