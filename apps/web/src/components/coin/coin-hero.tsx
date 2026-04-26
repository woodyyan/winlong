import { formatCompactCurrency, formatCurrency, formatPercent } from "@/lib/formatters";
import type { CoinSummary } from "@/lib/types";
import { RankBadge } from "@/components/pool/rank-badge";
import { ScoreBar } from "@/components/pool/score-bar";

export function CoinHero({ coin }: { coin: CoinSummary }) {
  return (
    <section className="panel rounded-[32px] p-6 lg:p-8">
      <div className="flex flex-col gap-6 md:flex-row md:items-start md:justify-between">
        <div className="flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-[24px] bg-indigo-500/16 text-2xl text-indigo-200 glow-ring">
            {coin.logoText}
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.32em] text-slate-500">{coin.symbol}</p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-100">{coin.name}</h1>
            <p className="mt-1 text-sm text-slate-400">{coin.nameZh}</p>
          </div>
        </div>

        <div className="md:text-right">
          <div className="font-mono text-4xl font-semibold text-slate-50">
            {formatCurrency(coin.price, coin.price < 5 ? 4 : 2)}
          </div>
          <div className={`mt-2 text-sm ${coin.change24h >= 0 ? "text-up" : "text-down"}`}>{formatPercent(coin.change24h)}</div>
        </div>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-[minmax(0,1.2fr)_minmax(260px,0.8fr)]">
        <div>
          <ScoreBar score={coin.totalScore} />
          <div className="mt-4 flex items-center gap-3 text-sm text-slate-400">
            <RankBadge rank={coin.rank} rankChange={coin.rankChange} />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-3 text-sm">
          <div className="rounded-3xl border border-white/6 bg-white/[0.03] p-4">
            <div className="metric-label">市值</div>
            <div className="metric-value mt-2">{formatCompactCurrency(coin.marketCap)}</div>
          </div>
          <div className="rounded-3xl border border-white/6 bg-white/[0.03] p-4">
            <div className="metric-label">24h 成交量</div>
            <div className="metric-value mt-2">{formatCompactCurrency(coin.volume24h)}</div>
          </div>
          <div className="rounded-3xl border border-white/6 bg-white/[0.03] p-4">
            <div className="metric-label">Open Interest</div>
            <div className="metric-value mt-2">{coin.openInterest ? formatCompactCurrency(coin.openInterest) : "—"}</div>
          </div>
        </div>
      </div>
    </section>
  );
}
