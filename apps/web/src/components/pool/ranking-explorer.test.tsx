import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { buildVisibleCoins, RankingExplorer } from "@/components/pool/ranking-explorer";
import type { StatusResponse, WinlongListResponse } from "@/lib/types";

const listFixture: WinlongListResponse["data"] = {
  computedAt: "2026-04-22T08:00:00Z",
  totalCoins: 2,
  returnedCount: 2,
  dataQuality: "full",
  coins: [
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
      change24h: 7.42,
      volume24h: 620000000,
      marketCap: 4100000000,
      totalScore: 75.6,
      rank: 2,
      rankChange: 4,
      factors: { momentum: 94, liquidity: 61, derivatives: 58, community: 80 },
      hasFutures: false,
      openInterest: null,
      fundingRate: null,
      longShortRatio: null,
      tags: ["ai"],
      updatedAt: "2026-04-22T08:00:00Z",
    },
  ],
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
  },
  sources: [],
  logs: [],
};

describe("buildVisibleCoins", () => {
  it("filters by search and ai tag", () => {
    expect(buildVisibleCoins(listFixture.coins, "tao", "all", []).map((coin) => coin.symbol)).toEqual(["TAOUSDT"]);
    expect(buildVisibleCoins(listFixture.coins, "", "ai", []).map((coin) => coin.symbol)).toEqual(["TAOUSDT"]);
  });
});

describe("RankingExplorer", () => {
  it("updates visible cards when searching", async () => {
    const user = userEvent.setup();
    render(<RankingExplorer initialList={listFixture} initialStatus={statusFixture} />);

    expect(screen.getByText("AI 排行 · Top 2")).toBeInTheDocument();
    const input = screen.getByPlaceholderText("搜索币种或标签");
    await user.type(input, "tao");

    expect(screen.getByText("AI 排行 · Top 1")).toBeInTheDocument();
  });
});
