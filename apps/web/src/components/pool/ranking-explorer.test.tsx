import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { buildVisibleCoins, RankingExplorer } from "@/components/pool/ranking-explorer";
import type { CoinSummary, PoolSummary, StatusResponse, WinlongListResponse } from "@/lib/types";
import { useWatchlistStore } from "@/store/watchlist-store";

const coinFixtures: CoinSummary[] = [
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
    rank: 1,
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
    reasonTags: ["OI 与波动共振", "成交量持续放大", "资金费率健康"],
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
    rank: 2,
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
    reasonTags: ["超跌偏离", "AI 主题活跃", "资金拥挤回落"],
    momentumDirection: null,
    meanReversionDirection: "rebound-long",
    lsGameDirection: null,
    tags: ["ai"],
    updatedAt: "2026-04-22T08:00:00Z",
  },
];

const poolFixtures: PoolSummary[] = [
  {
    key: "momentum",
    name: "冲浪池",
    shortName: "Momentum",
    description: "抓 OI 与波动同步放大的高活跃币。",
    count: 2,
    avgScore: 73.3,
    leaderSymbol: "BTCUSDT",
    leaderScore: 92.4,
    leaderDirection: "long continuation",
  },
  {
    key: "trend",
    name: "趋势池",
    shortName: "Trend",
    description: "筛选相关性稳定、资金结构健康的趋势币。",
    count: 2,
    avgScore: 63.6,
    leaderSymbol: "BTCUSDT",
    leaderScore: 78.1,
    leaderDirection: null,
  },
  {
    key: "meanReversion",
    name: "逆势池",
    shortName: "Reversion",
    description: "寻找情绪极值和 OI 释放后的反弹机会。",
    count: 2,
    avgScore: 58.2,
    leaderSymbol: "TAOUSDT",
    leaderScore: 84.8,
    leaderDirection: "rebound-long",
  },
  {
    key: "lsGame",
    name: "博弈池",
    shortName: "Squeeze",
    description: "寻找多空拥挤和潜在挤兑方向。",
    count: 2,
    avgScore: 48.3,
    leaderSymbol: "TAOUSDT",
    leaderScore: 52.4,
    leaderDirection: "two-way squeeze candidate",
  },
];

const listFixture: WinlongListResponse["data"] = {
  computedAt: "2026-04-22T08:00:00Z",
  totalCoins: 2,
  returnedCount: 2,
  dataQuality: "full",
  pools: poolFixtures,
  coins: coinFixtures,
};

const statusFixture: StatusResponse["data"] = {
  overview: {
    computedAt: "2026-04-22T08:00:00Z",
    lastScoreAt: "2026-04-22T08:00:00Z",
    nextScoreAt: "2026-04-22T12:00:00Z",
    refreshIntervalHours: 4,
    poolSize: 2,
    coinsWithFutures: 1,
    dataQuality: "full",
    databaseSizeMb: 1.2,
    uptime: "3天 7小时",
    runtimeData: true,
  },
  sources: [],
  logs: [],
};

describe("buildVisibleCoins", () => {
  it("filters by search and ai tag within active pool", () => {
    expect(buildVisibleCoins(coinFixtures, "tao", "all", [], "momentum").map((coin) => coin.symbol)).toEqual([]);
    expect(buildVisibleCoins(coinFixtures, "", "ai", [], "momentum").map((coin) => coin.symbol)).toEqual([]);
    expect(buildVisibleCoins(coinFixtures, "btc", "all", [], "trend").map((coin) => coin.symbol)).toEqual(["BTCUSDT"]);
  });

  it("filters by score, direction, and favorites using pool-specific fields", () => {
    expect(buildVisibleCoins(coinFixtures, "", "score80", [], "meanReversion").map((coin) => coin.symbol)).toEqual(["TAOUSDT"]);
    expect(buildVisibleCoins(coinFixtures, "", "directional", [], "meanReversion").map((coin) => coin.symbol)).toEqual(["TAOUSDT"]);
    expect(buildVisibleCoins(coinFixtures, "", "favorites", ["BTCUSDT"], "momentum").map((coin) => coin.symbol)).toEqual(["BTCUSDT"]);
  });
});

describe("RankingExplorer", () => {
  beforeEach(() => {
    useWatchlistStore.setState({ symbols: [] });
  });

  it("switches pools and updates the visible heading", async () => {
    const user = userEvent.setup();
    render(<RankingExplorer initialList={listFixture} initialStatus={statusFixture} />);

    expect(screen.getByRole("heading", { name: "冲浪池 · Top 1" })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /逆势池/i }));

    expect(screen.getByRole("heading", { name: "逆势池 · Top 1" })).toBeInTheDocument();
    expect(screen.getByText("比特张量")).toBeInTheDocument();
  });

  it("updates visible rows when searching inside the active pool", async () => {
    const user = userEvent.setup();
    render(<RankingExplorer initialList={listFixture} initialStatus={statusFixture} />);

    const input = screen.getByPlaceholderText("搜索币种或标签");
    await user.type(input, "tao");

    expect(screen.getByRole("heading", { name: "冲浪池 · Top 0" })).toBeInTheDocument();
  });

  it("shows overlapping members when a coin belongs to multiple pools", async () => {
    const user = userEvent.setup();
    render(<RankingExplorer initialList={listFixture} initialStatus={statusFixture} />);

    await user.click(screen.getByRole("button", { name: /趋势池/i }));

    expect(screen.getByRole("heading", { name: "趋势池 · Top 1" })).toBeInTheDocument();
    expect(screen.getByText("比特币")).toBeInTheDocument();
  });
});
