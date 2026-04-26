import { notFound } from "next/navigation";

import { FactorDetailGroups } from "@/components/coin/factor-detail-groups";
import { CoinHero } from "@/components/coin/coin-hero";
import { DerivativesPanel } from "@/components/coin/derivatives-panel";
import { FactorBreakdownChart } from "@/components/charts/factor-breakdown-chart";
import { FactorRadar } from "@/components/charts/factor-radar";
import { PriceChart } from "@/components/charts/price-chart";
import { ScoreHistoryChart } from "@/components/charts/score-history-chart";
import { getCoinDetail, getCoinHistory } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function CoinDetailPage({ params }: { params: Promise<{ symbol: string }> }) {
  const { symbol } = await params;

  try {
    const [detailResponse, historyResponse] = await Promise.all([
      getCoinDetail(symbol),
      getCoinHistory(symbol),
    ]);

    const detail = detailResponse.data;
    const history = historyResponse.data;

    return (
      <main className="page-shell space-y-6">
        <CoinHero coin={detail.coin} />

        <section className="grid gap-6 xl:grid-cols-[minmax(0,1.25fr)_minmax(360px,0.9fr)]">
          <div className="space-y-6">
            <section className="panel rounded-[32px] p-5 lg:p-6">
              <div className="mb-4 text-lg font-semibold text-slate-100">价格走势（近 30 天）</div>
              <PriceChart points={history} />
            </section>
            <section className="panel rounded-[32px] p-5 lg:p-6">
              <div className="mb-4 text-lg font-semibold text-slate-100">评分 / 排名趋势</div>
              <ScoreHistoryChart points={history} />
            </section>
            <FactorDetailGroups groups={detail.factorDetails} />
          </div>

          <div className="space-y-6">
            <section className="panel rounded-[32px] p-5 lg:p-6">
              <div className="mb-4 text-lg font-semibold text-slate-100">四类因子雷达图</div>
              <FactorRadar factors={detail.coin.factors} />
            </section>
            <section className="panel rounded-[32px] p-5 lg:p-6">
              <div className="mb-4 text-lg font-semibold text-slate-100">类别得分拆解</div>
              <FactorBreakdownChart groups={detail.factorDetails} />
            </section>
            <DerivativesPanel derivatives={detail.derivatives} />
          </div>
        </section>
      </main>
    );
  } catch {
    notFound();
  }
}
