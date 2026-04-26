"use client";

import ReactECharts from "echarts-for-react";

import { formatDateTime } from "@/lib/formatters";
import type { HistoryPoint } from "@/lib/types";

export function ScoreHistoryChart({ points }: { points: HistoryPoint[] }) {
  return (
    <ReactECharts
      style={{ height: 320 }}
      option={{
        backgroundColor: "transparent",
        tooltip: { trigger: "axis" },
        legend: { textStyle: { color: "#94a3b8" } },
        grid: { left: 48, right: 48, top: 36, bottom: 36 },
        xAxis: {
          type: "category",
          axisLabel: {
            color: "#64748b",
            formatter: (value: string) => formatDateTime(value),
          },
          data: points.map((point) => point.timestamp),
        },
        yAxis: [
          {
            type: "value",
            name: "评分",
            min: 60,
            max: 100,
            axisLabel: { color: "#94a3b8" },
            splitLine: { lineStyle: { color: "rgba(148,163,184,0.08)" } },
          },
          {
            type: "value",
            name: "排名",
            inverse: true,
            min: 1,
            max: 8,
            axisLabel: { color: "#94a3b8" },
            splitLine: { show: false },
          },
        ],
        series: [
          {
            name: "评分",
            type: "line",
            smooth: true,
            data: points.map((point) => point.score),
            lineStyle: { color: "#818cf8", width: 3 },
            itemStyle: { color: "#c4b5fd" },
          },
          {
            name: "排名",
            type: "line",
            smooth: true,
            yAxisIndex: 1,
            data: points.map((point) => point.rank),
            lineStyle: { color: "#f59e0b", width: 2 },
            itemStyle: { color: "#fbbf24" },
          },
        ],
      }}
    />
  );
}
