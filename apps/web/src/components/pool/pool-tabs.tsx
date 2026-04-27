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
            onClick={() => onSelect(pool.key)}
            className={`panel rounded-[28px] p-4 text-left transition ${
              active ? "border-cyan-400/30 bg-cyan-500/10" : "hover:border-white/12"
            }`}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="text-lg font-semibold text-slate-100">{pool.name}</div>
                <div className="text-xs uppercase tracking-[0.24em] text-cyan-200/80">{pool.shortName}</div>
              </div>
              <div className="rounded-full bg-white/[0.04] px-3 py-1 text-xs text-slate-300">{pool.count} 币</div>
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-400">{pool.description}</p>
          </button>
        );
      })}
    </div>
  );
}
