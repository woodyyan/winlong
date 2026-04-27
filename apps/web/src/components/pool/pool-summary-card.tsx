import { ArrowRightLeft, TrendingDown, TrendingUp, Waves } from "lucide-react";

import { formatTimeAgo } from "@/lib/formatters";
import type { PoolSummary, StatusOverview } from "@/lib/types";
import type { PoolKey } from "@/lib/pool-meta";

const poolIcons: Record<PoolKey, typeof Waves> = {
  momentum: Waves,
  trend: TrendingUp,
  meanReversion: TrendingDown,
  lsGame: ArrowRightLeft,
};

export function PoolSummaryCard({ summary, overview }: { summary: PoolSummary; overview: StatusOverview }) {
  const Icon = poolIcons[summary.key];

  return (
    <section className="panel rounded-[32px] p-5 lg:p-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-cyan-500/12 text-cyan-200">
              <Icon className="h-5 w-5" />
            </div>
            <div>
              <div className="text-xl font-semibold text-slate-100">{summary.name}</div>
              <div className="text-xs uppercase tracking-[0.24em] text-cyan-200/80">{summary.shortName}</div>
            </div>
          </div>
          <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-400">{summary.description}</p>
        </div>

        <div className="grid grid-cols-2 gap-3 text-sm lg:min-w-[320px]">
          <div className="rounded-3xl border border-white/6 bg-white/[0.03] p-4">
            <div className="metric-label">榜首</div>
            <div className="metric-value mt-2">{summary.leaderSymbol ?? "—"}</div>
            <div className="mt-2 text-xs text-slate-500">{summary.leaderDirection ?? "无方向标签"}</div>
          </div>
          <div className="rounded-3xl border border-white/6 bg-white/[0.03] p-4">
            <div className="metric-label">平均池分</div>
            <div className="metric-value mt-2">{summary.avgScore.toFixed(1)}</div>
            <div className="mt-2 text-xs text-slate-500">池内 {summary.count} 个币</div>
          </div>
          <div className="rounded-3xl border border-white/6 bg-white/[0.03] p-4">
            <div className="metric-label">数据状态</div>
            <div className="metric-value mt-2">{overview.runtimeData ? "实时" : "缓存"}</div>
            <div className="mt-2 text-xs text-slate-500">{overview.dataQuality}</div>
          </div>
          <div className="rounded-3xl border border-white/6 bg-white/[0.03] p-4">
            <div className="metric-label">更新时间</div>
            <div className="metric-value mt-2">{formatTimeAgo(overview.computedAt)}</div>
            <div className="mt-2 text-xs text-slate-500">下次 {overview.nextScoreAt.slice(11, 16)}</div>
          </div>
        </div>
      </div>
    </section>
  );
}
