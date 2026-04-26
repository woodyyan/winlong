import type { CoinFactors } from "@/lib/types";

const labels: Array<{ key: keyof CoinFactors; label: string }> = [
  { key: "momentum", label: "动" },
  { key: "liquidity", label: "流" },
  { key: "derivatives", label: "衍" },
  { key: "community", label: "社" },
];

export function FactorMiniBars({ factors }: { factors: CoinFactors }) {
  return (
    <div className="grid grid-cols-4 gap-2">
      {labels.map((item) => {
        const value = factors[item.key];
        return (
          <div key={item.key} className="rounded-2xl border border-white/6 bg-white/[0.03] p-2">
            <div className="flex items-center justify-between text-[11px] text-slate-400">
              <span>{item.label}</span>
              <span className="font-mono text-slate-200">{value.toFixed(0)}</span>
            </div>
            <div className="score-track mt-2 h-1.5 overflow-hidden rounded-full">
              <div className="h-full rounded-full bg-indigo-400" style={{ width: `${value}%` }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}
