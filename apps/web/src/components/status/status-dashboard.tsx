import { Activity, Database, ShieldAlert } from "lucide-react";

import { formatDateTime, formatTimeAgo } from "@/lib/formatters";
import type { StatusResponse } from "@/lib/types";

const sourceTone: Record<string, string> = {
  ok: "text-emerald-300 bg-emerald-500/10",
  stale: "text-amber-300 bg-amber-500/10",
  cached: "text-sky-300 bg-sky-500/10",
};

const qualityLabel: Record<string, string> = {
  full: "正常",
  degraded: "部分降级",
  cached: "缓存",
};

export function StatusDashboard({ data }: { data: StatusResponse["data"] }) {
  const qualityText = qualityLabel[data.overview.dataQuality] ?? data.overview.dataQuality;

  return (
    <main className="page-shell space-y-6">
      <section className="panel rounded-[32px] p-6 lg:p-8">
        <p className="text-xs uppercase tracking-[0.3em] text-slate-500">System status</p>
        <h1 className="mt-3 text-3xl font-semibold text-slate-50">评分调度、数据源健康度与最近日志</h1>
        <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-400">
          这一页先把第一版网站最关键的运行信息露出来，方便你后面接真实采集器时快速判断是接口问题、缓存问题还是评分任务没跑。
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <div className="panel rounded-[28px] p-5">
          <div className="flex items-center gap-2 text-slate-300"><Activity className="h-4 w-4 text-indigo-300" /> 上次评分</div>
          <div className="mt-3 text-2xl font-semibold text-slate-50">{formatTimeAgo(data.overview.lastScoreAt)}</div>
          <div className="mt-2 text-sm text-slate-400">下次刷新 {formatDateTime(data.overview.nextScoreAt)}</div>
        </div>
        <div className="panel rounded-[28px] p-5">
          <div className="flex items-center gap-2 text-slate-300"><Database className="h-4 w-4 text-indigo-300" /> 池内规模</div>
          <div className="mt-3 text-2xl font-semibold text-slate-50">{data.overview.poolSize} 个币</div>
          <div className="mt-2 text-sm text-slate-400">其中 {data.overview.coinsWithFutures} 个带衍生品数据</div>
        </div>
        <div className="panel rounded-[28px] p-5">
          <div className="flex items-center gap-2 text-slate-300"><ShieldAlert className="h-4 w-4 text-indigo-300" /> 数据质量</div>
          <div className="mt-3 text-2xl font-semibold text-slate-50">{qualityText}</div>
          <div className="mt-2 text-sm text-slate-400">数据库 {data.overview.databaseSizeMb.toFixed(2)} MB</div>
        </div>
        <div className="panel rounded-[28px] p-5">
          <div className="text-slate-300">运行时间</div>
          <div className="mt-3 text-2xl font-semibold text-slate-50">{data.overview.uptime}</div>
          <div className="mt-2 text-sm text-slate-400">周期 {data.overview.refreshIntervalHours} 小时 / 次</div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_420px]">
        <div className="panel rounded-[32px] p-6">
          <h2 className="text-xl font-semibold text-slate-100">数据源状态</h2>
          <div className="mt-4 space-y-4">
            {data.sources.map((source) => (
              <div key={source.source} className="rounded-3xl border border-white/6 bg-white/[0.03] p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <div className="text-lg font-medium text-slate-100">{source.source}</div>
                    <div className="mt-1 text-sm text-slate-400">{source.detail}</div>
                  </div>
                  <div className={`rounded-full px-3 py-1 text-xs ${sourceTone[source.status] ?? sourceTone.ok}`}>{source.status}</div>
                </div>
                <div className="mt-3 flex flex-wrap gap-4 text-sm text-slate-400">
                  <span>最近成功：{formatTimeAgo(source.lastSuccessAt)}</span>
                  <span>延迟：{source.latencyMs} ms</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="panel rounded-[32px] p-6">
          <h2 className="text-xl font-semibold text-slate-100">最近日志</h2>
          <div className="mt-4 space-y-3">
            {data.logs.map((log) => (
              <div key={`${log.timestamp}-${log.message}`} className="rounded-3xl border border-white/6 bg-white/[0.03] p-4">
                <div className="flex items-center justify-between text-xs uppercase tracking-[0.2em] text-slate-500">
                  <span>{log.level}</span>
                  <span>{formatDateTime(log.timestamp)}</span>
                </div>
                <div className="mt-2 text-sm text-slate-300">{log.message}</div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
