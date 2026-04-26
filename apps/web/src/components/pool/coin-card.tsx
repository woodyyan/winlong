"use client";

import Link from "next/link";
import { Star } from "lucide-react";

import { formatCompactCurrency, formatCurrency, formatPercent } from "@/lib/formatters";
import type { CoinSummary } from "@/lib/types";
import { useWatchlistStore } from "@/store/watchlist-store";
import { FactorMiniBars } from "@/components/pool/factor-mini-bars";
import { RankBadge } from "@/components/pool/rank-badge";
import { ScoreBar } from "@/components/pool/score-bar";

export function CoinCard({ coin }: { coin: CoinSummary }) {
  const symbols = useWatchlistStore((state) => state.symbols);
  const toggle = useWatchlistStore((state) => state.toggle);
  const isSaved = symbols.includes(coin.symbol);

  return (
    <article className="panel group rounded-[28px] p-4 transition hover:-translate-y-0.5 hover:border-indigo-400/20">
      <div className="mb-4 flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-500/14 text-xl text-indigo-200 glow-ring">
            {coin.logoText}
          </div>
          <div>
            <RankBadge rank={coin.rank} rankChange={coin.rankChange} />
            <p className="mt-1 text-sm text-slate-400">{coin.name} · {coin.nameZh}</p>
          </div>
        </div>
        <button
          type="button"
          aria-label={isSaved ? `取消关注 ${coin.symbol}` : `关注 ${coin.symbol}`}
          onClick={() => toggle(coin.symbol)}
          className="rounded-full border border-white/8 p-2 text-slate-400 transition hover:text-amber-300"
        >
          <Star className={`h-4 w-4 ${isSaved ? "fill-amber-300 text-amber-300" : ""}`} />
        </button>
      </div>

      <Link href={`/coin/${coin.symbol}`} className="block space-y-4">
        <div className="space-y-1">
          <div className="font-mono text-2xl font-semibold tracking-tight text-slate-100">
            {formatCurrency(coin.price, coin.price < 5 ? 4 : 2)}
          </div>
          <div className={coin.change24h >= 0 ? "text-up" : "text-down"}>{formatPercent(coin.change24h)}</div>
        </div>

        <ScoreBar score={coin.totalScore} />
        <FactorMiniBars factors={coin.factors} />

        <div className="grid grid-cols-3 gap-2 text-xs text-slate-400">
          <div className="rounded-2xl border border-white/6 bg-white/[0.02] p-3">
            <div className="metric-label">市值</div>
            <div className="metric-value">{formatCompactCurrency(coin.marketCap)}</div>
          </div>
          <div className="rounded-2xl border border-white/6 bg-white/[0.02] p-3">
            <div className="metric-label">24h 量</div>
            <div className="metric-value">{formatCompactCurrency(coin.volume24h)}</div>
          </div>
          <div className="rounded-2xl border border-white/6 bg-white/[0.02] p-3">
            <div className="metric-label">OI</div>
            <div className="metric-value">{coin.openInterest ? formatCompactCurrency(coin.openInterest) : "—"}</div>
          </div>
        </div>
      </Link>
    </article>
  );
}
