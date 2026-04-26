"use client";

import ReactECharts from "echarts-for-react";

import type { FactorCategoryDetail } from "@/lib/types";

export function FactorBreakdownChart({ groups }: { groups: FactorCategoryDetail[] }) {
  return (
    <ReactECharts
      style={{ height: 320 }}
      option={{
        backgroundColor: "transparent",
        grid: { left: 80, right: 10, top: 10, bottom: 20 },
        xAxis: {
          type: "value",
          axisLabel: { color: "#94a3b8" },
          splitLine: { lineStyle: { color: "rgba(148,163,184,0.08)" } },
        },
        yAxis: {
          type: "category",
          axisLabel: { color: "#cbd5e1" },
          data: groups.map((group) => group.label),
        },
        series: [
          {
            type: "bar",
            data: groups.map((group) => group.score),
            showBackground: true,
            backgroundStyle: { color: "rgba(148,163,184,0.08)" },
            itemStyle: {
              borderRadius: 999,
              color: "#6366f1",
            },
          },
        ],
      }}
    />
  );
}
