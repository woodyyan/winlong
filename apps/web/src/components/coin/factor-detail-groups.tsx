import type { FactorCategoryDetail } from "@/lib/types";

export function FactorDetailGroups({ groups }: { groups: FactorCategoryDetail[] }) {
  return (
    <section className="space-y-4">
      {groups.map((group) => (
        <article key={group.category} className="panel rounded-[28px] p-5">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-slate-100">{group.label}</h3>
              <p className="text-sm text-slate-400">类别得分 {group.score.toFixed(1)}</p>
            </div>
          </div>
          <div className="mt-4 space-y-3">
            {group.subFactors.map((factor) => (
              <div key={factor.key} className="rounded-3xl border border-white/6 bg-white/[0.03] p-4">
                <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                  <div>
                    <div className="font-medium text-slate-100">{factor.name}</div>
                    <div className="mt-1 text-sm leading-6 text-slate-400">{factor.explanation}</div>
                  </div>
                  <div className="shrink-0 text-right text-sm text-slate-400">
                    <div>原始值 {factor.rawValue.toFixed(2)}</div>
                    <div>Z-Score {factor.zScore.toFixed(2)}</div>
                    <div>权重 {(factor.weight * 100).toFixed(0)}%</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </article>
      ))}
    </section>
  );
}
