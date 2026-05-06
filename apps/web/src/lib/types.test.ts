import { describe, expect, it } from "vitest";

import type { CoinDetailResponse, CoinSummary, StatusResponse } from "@/lib/types";

describe("winlong frontend types", () => {
  it("accepts pool scoring fields on coin summary", () => {
    const coin: CoinSummary = {
      symbol: "BTCUSDT",
      baseAsset: "BTC",
      name: "Bitcoin",
      nameZh: "比特币",
      logoText: "BTC",
      price: 65000,
      change24h: 3.2,
      volume24h: 20000000000,
      marketCap: 1200000000000,
      totalScore: 88.1,
      rank: 1,
      rankChange: 1,
      factors: { momentum: 92, liquidity: 97, derivatives: 84, community: 75 },
      hasFutures: true,
      openInterest: 7800000000,
      fundingRate: 0.0001,
      longShortRatio: 1.08,
      primaryPool: "momentum",
      primaryScore: 91.4,
      poolScores: {
        momentum: 91.4,
        trend: 71.2,
        meanReversion: 36.8,
        lsGame: 48.2,
      },
      reasonTags: ["24h/4h OI 变化 18.00% / 6.00%"],
      tags: ["core"],
      updatedAt: "2026-04-27T00:00:00Z",
    };

    expect(coin.primaryPool).toBe("momentum");
    expect(coin.poolScores.lsGame).toBeGreaterThan(0);
  });

  it("accepts market feature snapshot on coin detail response", () => {
    const detail: CoinDetailResponse = {
      code: 0,
      message: "ok",
      data: {
        coin: {
          symbol: "ETHUSDT",
          baseAsset: "ETH",
          name: "Ethereum",
          nameZh: "以太坊",
          logoText: "ETH",
          price: 3200,
          change24h: -2,
          volume24h: 9000000000,
          marketCap: 400000000000,
          totalScore: 80,
          rank: 2,
          rankChange: 0,
          factors: { momentum: 68, liquidity: 92, derivatives: 84, community: 73 },
          hasFutures: true,
          openInterest: 4500000000,
          fundingRate: -0.00002,
          longShortRatio: 0.97,
          primaryPool: "meanReversion",
          primaryScore: 77.1,
          poolScores: { momentum: 52, trend: 61, meanReversion: 77.1, lsGame: 58 },
          reasonTags: ["均线偏离 -6.20%"],
          tags: ["smart-contract"],
          updatedAt: "2026-04-27T00:00:00Z",
        },
        factorDetails: [],
        derivatives: {
          hasFutures: true,
          openInterest: 4500000000,
          fundingRate: -0.00002,
          longShortRatio: 0.97,
          oiChange24h: -12.1,
          recentFundingRates: [-0.00003, -0.00002],
        },
        marketFeatures: {
          oiChange1h: -1.2,
          oiChange4h: -4.8,
          oiChange24h: -12.1,
          turnover24h: 0.0225,
          oiToVolume: 0.5,
          oiToMarketcap: 0.011,
          corrBtc7d: 0.78,
          corrEth7d: 1,
          fundingRateMean24h: -0.00002,
          fundingRateStd24h: 0.00001,
          priceChange1h: -0.7,
          priceChange24h: -2,
          distanceToMa20: -6.2,
          priceVolatility7d: 3.1,
          longShortRatioStability: 0.04,
          oiStability7d: 1.6,
          liquidationToOi24h: 0.09,
          liquidationToVolume24h: 0.03,
        },
      },
    };

    expect(detail.data.marketFeatures?.distanceToMa20).toBeLessThan(0);
  });

  it("accepts runtimeData on status response", () => {
    const status: StatusResponse = {
      code: 0,
      message: "ok",
      data: {
        overview: {
          computedAt: "2026-04-27T00:00:00Z",
          lastScoreAt: "2026-04-27T00:00:00Z",
          nextScoreAt: "2026-04-27T00:15:00Z",
          refreshIntervalHours: 0.25,
          poolSize: 120,
          coinsWithFutures: 120,
          dataQuality: "full",
          databaseSizeMb: 4.2,
          uptime: "实时同步",
          runtimeData: true,
        },
        sources: [],
        logs: [],
      },
    };

    expect(status.data.overview.runtimeData).toBe(true);
  });
});
