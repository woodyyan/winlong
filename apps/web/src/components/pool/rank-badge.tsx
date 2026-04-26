import { Minus, TrendingDown, TrendingUp } from "lucide-react";

export function RankBadge({ rank, rankChange }: { rank: number; rankChange: number }) {
  return (
    <div className="flex items-center gap-2">
      <div className="text-2xl font-semibold tracking-tight text-slate-100">#{rank}</div>
      <div className="flex items-center gap-1 text-xs text-slate-400">
        {rankChange > 0 ? (
          <>
            <TrendingUp className="h-3.5 w-3.5 text-emerald-400" />
            <span className="text-emerald-300">+{rankChange}</span>
          </>
        ) : rankChange < 0 ? (
          <>
            <TrendingDown className="h-3.5 w-3.5 text-rose-400" />
            <span className="text-rose-300">{rankChange}</span>
          </>
        ) : (
          <>
            <Minus className="h-3.5 w-3.5" />
            <span>持平</span>
          </>
        )}
      </div>
    </div>
  );
}
