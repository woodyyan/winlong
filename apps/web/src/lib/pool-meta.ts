import type { CoinSummary, PoolSummary } from "@/lib/types";

export type PoolKey = "momentum" | "trend" | "meanReversion" | "lsGame";

export const POOL_ORDER: PoolKey[] = ["momentum", "trend", "meanReversion", "lsGame"];

export const POOL_META: Record<PoolKey, { name: string; shortName: string; description: string }> = {
  momentum: {
    name: "冲浪池",
    shortName: "Momentum",
    description: "抓 OI 与波动同步放大的高活跃币。",
  },
  trend: {
    name: "趋势池",
    shortName: "Trend",
    description: "筛选相关性稳定、资金结构健康的趋势币。",
  },
  meanReversion: {
    name: "逆势池",
    shortName: "Reversion",
    description: "寻找情绪极值和 OI 释放后的反弹机会。",
  },
  lsGame: {
    name: "博弈池",
    shortName: "Squeeze",
    description: "寻找多空拥挤和潜在挤兑方向。",
  },
};

export function getPoolScore(coin: CoinSummary, pool: PoolKey): number {
  return coin.poolScores[pool] ?? 0;
}

export function getPoolDirection(coin: CoinSummary, pool: PoolKey): string | null {
  if (pool === "momentum") {
    return coin.momentumDirection ?? null;
  }
  if (pool === "meanReversion") {
    return coin.meanReversionDirection ?? null;
  }
  if (pool === "lsGame") {
    return coin.lsGameDirection ?? null;
  }
  return null;
}

export function buildFallbackPoolSummaries(coins: CoinSummary[]): PoolSummary[] {
  return POOL_ORDER.map((pool) => {
    const members = coins.filter((coin) => coin.poolMemberships.includes(pool));
    const ranked = sortCoinsByPool(members, pool);
    const leader = ranked[0];
    return {
      key: pool,
      name: POOL_META[pool].name,
      shortName: POOL_META[pool].shortName,
      description: POOL_META[pool].description,
      count: ranked.length,
      avgScore: ranked.length ? Number((ranked.reduce((sum, coin) => sum + getPoolScore(coin, pool), 0) / ranked.length).toFixed(1)) : 0,
      leaderSymbol: leader?.symbol ?? null,
      leaderScore: leader ? getPoolScore(leader, pool) : null,
      leaderDirection: leader ? getPoolDirection(leader, pool) : null,
    };
  });
}

export function sortCoinsByPool(coins: CoinSummary[], pool: PoolKey): CoinSummary[] {
  return [...coins].sort((left, right) => {
    const diff = getPoolScore(right, pool) - getPoolScore(left, pool);
    if (diff !== 0) {
      return diff;
    }
    return left.rank - right.rank;
  });
}
