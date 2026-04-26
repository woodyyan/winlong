"use client";

import ReactECharts from "echarts-for-react";

import type { CoinFactors } from "@/lib/types";

export function FactorRadar({ factors }: { factors: CoinFactors }) {
  return (
    <ReactECharts
      style={{ height: 320 }}
      option={{
        backgroundColor: "transparent",
        radar: {
          radius: "68%",
          indicator: [
            { name: "动量", max: 100 },
            { name: "流动性", max: 100 },
            { name: "衍生品", max: 100 },
            { name: "社区", max: 100 },
          ],
          splitLine: { lineStyle: { color: "rgba(148,163,184,0.14)" } },
          splitArea: { areaStyle: { color: ["rgba(15,23,42,0.2)"] } },
          axisName: { color: "#cbd5e1" },
        },
        series: [
          {
            type: "radar",
            data: [
              {
                value: [factors.momentum, factors.liquidity, factors.derivatives, factors.community],
                areaStyle: { color: "rgba(99,102,241,0.24)" },
                lineStyle: { color: "#818cf8", width: 2 },
                itemStyle: { color: "#c4b5fd" },
              },
            ],
          },
        ],
      }}
    />
  );
}
