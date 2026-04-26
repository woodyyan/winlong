import { DatabaseZap } from "lucide-react";

import { formatDateTime, formatTimeAgo } from "@/lib/formatters";
import type { StatusOverview } from "@/lib/types";

const qualityTone: Record<string, string> = {
  full: "bg-emerald-500/12 text-emerald-300",
  degraded: "bg-amber-500/12 text-amber-300",
  cached: "bg-sky-500/12 text-sky-300",
};

const qualityLabel: Record<string, string> = {
  full: "正常",
  degraded: "部分降级",
  cached: "缓存",
};

export function StatusBar({ overview }: { overview: StatusOverview }) {
  const qualityClass = qualityTone[overview.dataQuality] ?? qualityTone.full;
  const qualityText = qualityLabel[overview.dataQuality] ?? overview.dataQuality;

  return (
    <section className="panel rounded-3xl p-4 md:p-5">
      <div className="space-y-2">
        <div className="flex items-center gap-2 text-sm text-slate-300">
          <DatabaseZap className="h-4 w-4 text-indigo-300" />
          当前池内 {overview.poolSize} 个币种，{overview.coinsWithFutures} 个含合约情绪数据
        </div>
        <div className="flex flex-wrap items-center gap-2 text-sm text-slate-400">
          <span className={`rounded-full px-3 py-1 text-xs ${qualityClass}`}>{qualityText}</span>
          <span>更新于 {formatTimeAgo(overview.computedAt)}</span>
          <span>下次评分 {formatDateTime(overview.nextScoreAt)}</span>
        </div>
      </div>
    </section>
  );
}
