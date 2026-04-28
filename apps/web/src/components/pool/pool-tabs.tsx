"use client";

import type { PoolSummary } from "@/lib/types";
import type { PoolKey } from "@/lib/pool-meta";

export function PoolTabs({
  pools,
  activePool,
  onSelect,
}: {
  pools: PoolSummary[];
  activePool: PoolKey;
  onSelect: (pool: PoolKey) => void;
}) {
  return (
    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
      {pools.map((pool) => {
        const active = pool.key === activePool;
        return (
          <button
            key={pool.key}
            type="button"
            aria-pressed={active}
            onClick={() => onSelect(pool.key)}
            className={`panel rounded-[28px] p-4 text-left transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300/60 ${
              active
                ? "border-cyan-300/70 bg-cyan-500/16 shadow-[0_0_0_1px_rgba(125,211,252,0.22),0_18px_40px_rgba(8,145,178,0.18)]"
                : "hover:border-white/12"
            }`}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <div className={`text-lg font-semibold ${active ? "text-cyan-100" : "text-slate-100"}`}>{pool.name}</div>
                </div>
                <div className={`text-xs uppercase tracking-[0.24em] ${active ? "text-cyan-100" : "text-cyan-200/80"}`}>
                  {pool.shortName}
                </div>
              </div>
              <div className={`rounded-full px-3 py-1 text-xs ${active ? "bg-cyan-400/12 text-cyan-100" : "bg-white/[0.04] text-slate-300"}`}>
                {pool.count} 币
              </div>
            </div>
            <p className={`mt-3 text-sm leading-6 ${active ? "text-slate-200" : "text-slate-400"}`}>{pool.description}</p>
          </button>
        );
      })}
    </div>
  );
}
