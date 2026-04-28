import { describe, expect, it } from "vitest";

import { buildFallbackPoolSummaries, sortCoinsByPool } from "@/lib/pool-meta";
import type { CoinSummary } from "@/lib/types";

const coins: CoinSummary[] = [
  {
    symbol: "BTCUSDT",
    baseAsset: "BTC",
    name: "Bitcoin",
    nameZh: "比特币",
    logoText: "₿",
    price: 97500,
    change24h: 2.35,
    volume24h: 28500000000,
    marketCap: 1920000000000,
    totalScore: 87.5,
    rank: 5,
    rankChange: 0,
    factors: { momentum: 85, liquidity: 98, derivatives: 78, community: 90 },
    hasFutures: true,
    openInterest: 12000000000,
    fundingRate: 0.0001,
    longShortRatio: 1.85,
    primaryPool: "momentum",
    primaryScore: 92.4,
    poolMemberships: ["momentum", "trend"],
    poolScores: { momentum: 92.4, trend: 78.1, meanReversion: 31.5, lsGame: 44.2 },
    reasonTags: ["OI 与波动共振"],
    momentumDirection: "long continuation",
    meanReversionDirection: "wait pullback",
    lsGameDirection: "two-way squeeze candidate",
    tags: ["core"],
    updatedAt: "2026-04-22T08:00:00Z",
  },
  {
    symbol: "TAOUSDT",
    baseAsset: "TAO",
    name: "Bittensor",
    nameZh: "比特张量",
    logoText: "τ",
    price: 488,
    change24h: -7.42,
    volume24h: 620000000,
    marketCap: 4100000000,
    totalScore: 75.6,
    rank: 1,
    rankChange: 4,
    factors: { momentum: 61, liquidity: 58, derivatives: 72, community: 80 },
    hasFutures: false,
    openInterest: null,
    fundingRate: null,
    longShortRatio: null,
    primaryPool: "meanReversion",
    primaryScore: 84.8,
    poolMemberships: ["meanReversion", "lsGame"],
    poolScores: { momentum: 54.2, trend: 49.1, meanReversion: 84.8, lsGame: 52.4 },
    reasonTags: ["超跌偏离"],
    momentumDirection: null,
    meanReversionDirection: "rebound-long",
    lsGameDirection: null,
    tags: ["ai"],
    updatedAt: "2026-04-22T08:00:00Z",
  },
];

describe("sortCoinsByPool", () => {
  it("sorts by active pool score instead of global rank", () => {
    expect(sortCoinsByPool(coins, "momentum").map((coin) => coin.symbol)).toEqual(["BTCUSDT", "TAOUSDT"]);
    expect(sortCoinsByPool(coins, "meanReversion").map((coin) => coin.symbol)).toEqual(["TAOUSDT", "BTCUSDT"]);
  });
});

describe("buildFallbackPoolSummaries", () => {
  it("counts overlapping memberships instead of only primary pool", () => {
    const summaries = buildFallbackPoolSummaries(coins);

    expect(summaries.find((summary) => summary.key === "momentum")?.count).toBe(1);
    expect(summaries.find((summary) => summary.key === "trend")?.count).toBe(1);
    expect(summaries.find((summary) => summary.key === "meanReversion")?.count).toBe(1);
    expect(summaries.find((summary) => summary.key === "lsGame")?.count).toBe(1);
  });
});
