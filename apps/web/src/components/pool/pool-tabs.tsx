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
            className={`panel rounded-[28px] p-4 text-left transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300/70 ${
              active
                ? "border-2 border-cyan-200 bg-[linear-gradient(135deg,rgba(34,211,238,0.20),rgba(14,165,233,0.14)_45%,rgba(6,182,212,0.06))] shadow-[0_0_0_1px_rgba(186,230,253,0.30),0_22px_48px_rgba(8,145,178,0.22)] -translate-y-1"
                : "border border-white/8 hover:border-white/16 hover:bg-white/[0.05]"
            }`}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <div className={`text-lg font-semibold ${active ? "text-white" : "text-slate-100"}`}>{pool.name}</div>
                </div>
                <div className={`text-xs uppercase tracking-[0.24em] ${active ? "text-cyan-50" : "text-cyan-200/80"}`}>
                  {pool.shortName}
                </div>
              </div>
              <div className={`rounded-full px-3 py-1 text-xs ${active ? "bg-white/16 text-white ring-1 ring-cyan-100/60" : "bg-white/[0.04] text-slate-300"}`}>
                {pool.count} 币
              </div>
            </div>
            <p className={`mt-3 text-sm leading-6 ${active ? "text-slate-50" : "text-slate-400"}`}>{pool.description}</p>
          </button>
        );
      })}
    </div>
  );
}
