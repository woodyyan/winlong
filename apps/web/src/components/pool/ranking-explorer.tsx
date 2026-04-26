"use client";

import React, { useMemo, useState } from "react";
import useSWR from "swr";

import { CoinCard } from "@/components/pool/coin-card";
import { RankingTable } from "@/components/pool/ranking-table";
import { StatusBar } from "@/components/layout/status-bar";
import { clientFetcher } from "@/lib/api";
import type { CoinSummary, StatusResponse, WinlongListResponse } from "@/lib/types";
import { useWatchlistStore } from "@/store/watchlist-store";

export type FilterKey = "all" | "favorites" | "momentum" | "liquidity" | "ai" | "movers";

const filters: Array<{ key: FilterKey; label: string }> = [
  { key: "all", label: "全部" },
  { key: "favorites", label: "自选" },
  { key: "momentum", label: "动量强" },
  { key: "liquidity", label: "高流动" },
  { key: "ai", label: "AI 主题" },
  { key: "movers", label: "排名上升" },
];

export function buildVisibleCoins(
  coins: CoinSummary[],
  search: string,
  filter: FilterKey,
  favorites: string[],
): CoinSummary[] {
  const keyword = search.trim().toLowerCase();

  return coins.filter((coin) => {
    const matchesSearch =
      keyword.length === 0 ||
      coin.symbol.toLowerCase().includes(keyword) ||
      coin.name.toLowerCase().includes(keyword) ||
      coin.nameZh.toLowerCase().includes(keyword) ||
      coin.tags.some((tag) => tag.toLowerCase().includes(keyword));

    const matchesFilter =
      filter === "all" ||
      (filter === "favorites" && favorites.includes(coin.symbol)) ||
      (filter === "momentum" && coin.factors.momentum >= 85) ||
      (filter === "liquidity" && coin.factors.liquidity >= 85) ||
      (filter === "ai" && coin.tags.includes("ai")) ||
      (filter === "movers" && coin.rankChange > 0);

    return matchesSearch && matchesFilter;
  });
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

  const coins = listResponse?.data.coins ?? initialList.coins;
  const status = statusResponse?.data ?? initialStatus;
  const visibleCoins = useMemo(
    () => buildVisibleCoins(coins, search, activeFilter, favorites),
    [activeFilter, coins, favorites, search],
  );

  return (
    <main className="page-shell space-y-6">
      <StatusBar overview={status.overview} />

      <section className="space-y-4">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h2 className="text-2xl font-semibold text-slate-100">AI 排行 · Top {visibleCoins.length}</h2>
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
          {visibleCoins.map((coin) => (
            <CoinCard key={coin.symbol} coin={coin} />
          ))}
        </div>

        <RankingTable coins={visibleCoins} />
      </section>
    </main>
  );
}
