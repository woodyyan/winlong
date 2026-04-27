import { formatCompactCurrency, formatCurrency, formatPercent } from "@/lib/formatters";
import type { CoinSummary } from "@/lib/types";
import { POOL_META, type PoolKey } from "@/lib/pool-meta";
import { RankBadge } from "@/components/pool/rank-badge";
import { getPoolDirectionLabel } from "@/components/pool/pool-helpers";
import { ScoreBar } from "@/components/pool/score-bar";

const poolOrder: PoolKey[] = ["momentum", "trend", "meanReversion", "lsGame"];

function getPrimaryPoolName(coin: CoinSummary) {
  if (!coin.primaryPool) {
    return "未归类";
  }
  return POOL_META[coin.primaryPool].name;
}

export function CoinHero({ coin }: { coin: CoinSummary }) {
  const primaryPool = coin.primaryPool ?? null;

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
            <div className="mt-3 flex flex-wrap gap-2">
              <span className="rounded-full bg-cyan-500/10 px-3 py-1 text-xs text-cyan-200">当前主池：{getPrimaryPoolName(coin)}</span>
              {coin.reasonTags.slice(0, 2).map((tag) => (
                <span key={tag} className="rounded-full border border-cyan-400/14 bg-cyan-500/8 px-3 py-1 text-xs text-slate-200">
                  {tag}
                </span>
              ))}
            </div>
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
        <div className="space-y-4">
          <ScoreBar score={coin.totalScore} label="总分" />
          <div className="mt-4 flex items-center gap-3 text-sm text-slate-400">
            <RankBadge rank={coin.rank} rankChange={coin.rankChange} />
          </div>
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            {poolOrder.map((pool) => (
              <div
                key={pool}
                className={`rounded-3xl border p-4 ${
                  primaryPool === pool ? "border-cyan-400/24 bg-cyan-500/8" : "border-white/6 bg-white/[0.03]"
                }`}
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="metric-label">{POOL_META[pool].name}</div>
                  {primaryPool === pool ? (
                    <span className="rounded-full bg-cyan-500/10 px-2 py-1 text-[11px] text-cyan-200">主池</span>
                  ) : null}
                </div>
                <div className="metric-value mt-2">{(coin.poolScores[pool] ?? 0).toFixed(1)}</div>
                <div className="mt-2 text-xs text-slate-500">{POOL_META[pool].shortName}</div>
                <div className="mt-2 text-xs text-slate-400">{getPoolDirectionLabel(coin, pool)}</div>
              </div>
            ))}
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
