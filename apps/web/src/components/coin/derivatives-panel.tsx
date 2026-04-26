import { formatCompactCurrency, formatPercent } from "@/lib/formatters";
import type { DerivativesPanel as DerivativesPanelType } from "@/lib/types";

export function DerivativesPanel({ derivatives }: { derivatives: DerivativesPanelType }) {
  if (!derivatives.hasFutures) {
    return (
      <section className="panel rounded-[32px] p-6 text-sm text-slate-400">
        当前 V1 数据里，这个币种没有合约情绪样本，所以衍生品区块用市场均值处理，不对总分做额外奖励或惩罚。
      </section>
    );
  }

  return (
    <section className="panel rounded-[32px] p-6">
      <div className="mb-4 text-lg font-semibold text-slate-100">衍生品情绪面板</div>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-3xl border border-white/6 bg-white/[0.03] p-4">
          <div className="metric-label">Open Interest</div>
          <div className="metric-value mt-2">{derivatives.openInterest ? formatCompactCurrency(derivatives.openInterest) : "—"}</div>
          <div className="mt-2 text-sm text-slate-400">24h 变化 {derivatives.oiChange24h ? formatPercent(derivatives.oiChange24h * 100) : "—"}</div>
        </div>
        <div className="rounded-3xl border border-white/6 bg-white/[0.03] p-4">
          <div className="metric-label">资金费率 / 多空比</div>
          <div className="metric-value mt-2">
            {derivatives.fundingRate !== null ? `${(derivatives.fundingRate * 100).toFixed(3)}%` : "—"}
          </div>
          <div className="mt-2 text-sm text-slate-400">Top Trader 多空比 {derivatives.longShortRatio?.toFixed(2) ?? "—"}</div>
        </div>
      </div>

      <div className="mt-4 rounded-3xl border border-white/6 bg-white/[0.03] p-4">
        <div className="metric-label">近 6 期资金费率</div>
        <div className="mt-3 flex flex-wrap gap-2">
          {derivatives.recentFundingRates.map((rate, index) => (
            <span key={`${rate}-${index}`} className="rounded-full bg-indigo-500/10 px-3 py-1 text-xs text-indigo-200">
              {(rate * 100).toFixed(3)}%
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
