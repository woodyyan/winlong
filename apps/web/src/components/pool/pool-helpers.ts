import { formatCompactCurrency, formatPercent } from "@/lib/formatters";
import type { CoinSummary } from "@/lib/types";
import type { PoolKey } from "@/lib/pool-meta";

export function getPoolDirectionLabel(coin: CoinSummary, pool: PoolKey): string {
  if (pool === "momentum") {
    return coin.momentumDirection ?? "long";
  }
  if (pool === "meanReversion") {
    return coin.meanReversionDirection ?? "rebound-long";
  }
  if (pool === "lsGame") {
    return coin.lsGameDirection ?? "two-way squeeze candidate";
  }
  return "trend-follow";
}

export function getPoolMetricChips(coin: CoinSummary, pool: PoolKey): Array<{ label: string; value: string }> {
  if (pool === "momentum") {
    return [
      { label: "24h", value: formatPercent(coin.change24h) },
      { label: "量能", value: formatCompactCurrency(coin.volume24h) },
      { label: "主池分", value: `${(coin.poolScores.momentum ?? 0).toFixed(1)}` },
    ];
  }
  if (pool === "trend") {
    return [
      { label: "总分", value: `${coin.totalScore.toFixed(1)}` },
      { label: "市值", value: formatCompactCurrency(coin.marketCap) },
      { label: "趋势分", value: `${(coin.poolScores.trend ?? 0).toFixed(1)}` },
    ];
  }
  if (pool === "meanReversion") {
    return [
      { label: "24h", value: formatPercent(coin.change24h) },
      { label: "方向", value: getPoolDirectionLabel(coin, pool) },
      { label: "逆势分", value: `${(coin.poolScores.meanReversion ?? 0).toFixed(1)}` },
    ];
  }
  return [
    { label: "方向", value: getPoolDirectionLabel(coin, pool) },
    { label: "OI", value: coin.openInterest ? formatCompactCurrency(coin.openInterest) : "—" },
    { label: "博弈分", value: `${(coin.poolScores.lsGame ?? 0).toFixed(1)}` },
  ];
}
