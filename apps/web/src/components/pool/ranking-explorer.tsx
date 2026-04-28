"use client";

import React, { useMemo, useState } from "react";
import useSWR from "swr";

import { CoinCard } from "@/components/pool/coin-card";
import { PoolTabs } from "@/components/pool/pool-tabs";
import { RankingTable } from "@/components/pool/ranking-table";
import { StatusBar } from "@/components/layout/status-bar";
import { clientFetcher } from "@/lib/api";
import { buildFallbackPoolSummaries, sortCoinsByPool, type PoolKey } from "@/lib/pool-meta";
import type { CoinSummary, PoolSummary, StatusResponse, WinlongListResponse } from "@/lib/types";
import { useWatchlistStore } from "@/store/watchlist-store";

export type FilterKey = "all" | "favorites" | "score80" | "directional" | "ai" | "movers";

const filters: Array<{ key: FilterKey; label: string }> = [
  { key: "all", label: "全部" },
  { key: "favorites", label: "自选" },
  { key: "score80", label: "分数 > 80" },
  { key: "directional", label: "方向明确" },
  { key: "ai", label: "AI 主题" },
  { key: "movers", label: "排名上升" },
];

function hasDirection(coin: CoinSummary, pool: PoolKey) {
  if (pool === "momentum") {
    return Boolean(coin.momentumDirection);
  }
  if (pool === "meanReversion") {
    return Boolean(coin.meanReversionDirection);
  }
  if (pool === "lsGame") {
    return Boolean(coin.lsGameDirection);
  }
  return true;
}

export function buildVisibleCoins(
  coins: CoinSummary[],
  search: string,
  filter: FilterKey,
  favorites: string[],
  activePool: PoolKey,
): CoinSummary[] {
  const poolMembers = coins.filter((coin) => coin.poolMemberships.includes(activePool));
  const keyword = search.trim().toLowerCase();

  return poolMembers.filter((coin) => {
    const matchesSearch =
      keyword.length === 0 ||
      coin.symbol.toLowerCase().includes(keyword) ||
      coin.name.toLowerCase().includes(keyword) ||
      coin.nameZh.toLowerCase().includes(keyword) ||
      coin.tags.some((tag) => tag.toLowerCase().includes(keyword));

    const poolScore = coin.poolScores[activePool] ?? coin.primaryScore ?? 0;
    const matchesFilter =
      filter === "all" ||
      (filter === "favorites" && favorites.includes(coin.symbol)) ||
      (filter === "score80" && poolScore >= 80) ||
      (filter === "directional" && hasDirection(coin, activePool)) ||
      (filter === "ai" && coin.tags.includes("ai")) ||
      (filter === "movers" && coin.rankChange > 0);

    return matchesSearch && matchesFilter;
  });
}

function normalizePools(list: WinlongListResponse["data"]): PoolSummary[] {
  return list.pools.length > 0 ? list.pools : buildFallbackPoolSummaries(list.coins);
}

export function RankingExplorer({
  initialList,
  initialStatus,
}: {
  initialList: WinlongListResponse["data"];
  initialStatus: StatusResponse["data"];
}) {
  const [search, setSearch] = useState("");
  const [activeFilter, setActiveFilter] = useState<FilterKey>("all");
  const [activePool, setActivePool] = useState<PoolKey>("momentum");
  const favorites = useWatchlistStore((state) => state.symbols);

  const { data: listResponse } = useSWR<WinlongListResponse>(
    "/api/winlong/list?sort_by=score&order=desc",
    clientFetcher,
    {
      fallbackData: { code: 0, message: "ok", data: initialList },
      revalidateOnMount: false,
      revalidateOnFocus: false,
      revalidateIfStale: false,
    },
  );

  const { data: statusResponse } = useSWR<StatusResponse>("/api/winlong/status", clientFetcher, {
    fallbackData: { code: 0, message: "ok", data: initialStatus },
    revalidateOnMount: false,
    revalidateOnFocus: false,
    revalidateIfStale: false,
  });

  const listData = listResponse?.data ?? initialList;
  const coins = listData.coins;
  const status = statusResponse?.data ?? initialStatus;
  const pools = useMemo(() => normalizePools(listData), [listData]);
  const activeSummary = pools.find((pool) => pool.key === activePool) ?? pools[0];
  const poolCoins = useMemo(() => sortCoinsByPool(coins, activePool), [activePool, coins]);
  const visibleCoins = useMemo(
    () => buildVisibleCoins(poolCoins, search, activeFilter, favorites, activePool),
    [activeFilter, activePool, favorites, poolCoins, search],
  );

  return (
    <main className="page-shell space-y-6">
      <StatusBar overview={status.overview} />
      <PoolTabs pools={pools} activePool={activePool} onSelect={setActivePool} />

      <section className="space-y-4">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h2 className="text-2xl font-semibold text-slate-100">
              {activeSummary?.name ?? "币种池"} · Top {visibleCoins.length}
            </h2>
          </div>
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="搜索币种或标签"
            className="w-full rounded-2xl border border-white/8 bg-white/[0.03] px-4 py-3 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-indigo-400/30 lg:max-w-xs"
          />
        </div>

        <div className="flex gap-2 overflow-x-auto pb-1">
          {filters.map((filter) => {
            const active = activeFilter === filter.key;
            return (
              <button
                key={filter.key}
                type="button"
                onClick={() => setActiveFilter(filter.key)}
                className={`shrink-0 rounded-full px-4 py-2 text-sm transition ${
                  active ? "bg-indigo-500/14 text-indigo-200" : "bg-white/[0.03] text-slate-400"
                }`}
              >
                {filter.label}
              </button>
            );
          })}
        </div>

        <div className="grid gap-4 lg:hidden">
          {visibleCoins.map((coin, index) => (
            <CoinCard key={coin.symbol} coin={coin} activePool={activePool} displayRank={index + 1} />
          ))}
        </div>

        <RankingTable coins={visibleCoins} activePool={activePool} />
      </section>
    </main>
  );
}
