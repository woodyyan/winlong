"use client";

import { useEffect, useRef } from "react";
import { AreaSeries, ColorType, createChart } from "lightweight-charts";

import type { HistoryPoint } from "@/lib/types";

export function PriceChart({ points }: { points: HistoryPoint[] }) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!containerRef.current || points.length === 0) return;

    const chart = createChart(containerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: "#94a3b8",
      },
      grid: {
        vertLines: { color: "rgba(148,163,184,0.08)" },
        horzLines: { color: "rgba(148,163,184,0.08)" },
      },
      crosshair: {
        vertLine: { color: "rgba(99,102,241,0.4)" },
        horzLine: { color: "rgba(99,102,241,0.4)" },
      },
      rightPriceScale: {
        borderColor: "rgba(148,163,184,0.14)",
      },
      timeScale: {
        borderColor: "rgba(148,163,184,0.14)",
      },
      width: containerRef.current.clientWidth,
      height: 320,
    });

    const series = chart.addSeries(AreaSeries, {
      lineColor: "#818cf8",
      topColor: "rgba(129,140,248,0.35)",
      bottomColor: "rgba(129,140,248,0.02)",
    });

    series.setData(
      points.map((point) => ({
        time: point.timestamp.slice(0, 10),
        value: point.price,
      })),
    );

    chart.timeScale().fitContent();

    const resizeObserver = new ResizeObserver(() => {
      if (!containerRef.current) return;
      chart.applyOptions({ width: containerRef.current.clientWidth });
    });
    resizeObserver.observe(containerRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
    };
  }, [points]);

  return <div ref={containerRef} className="h-80 w-full" />;
}
