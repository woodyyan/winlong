"use client";

import Link from "next/link";
import { createColumnHelper, flexRender, getCoreRowModel, useReactTable } from "@tanstack/react-table";

import { getPoolDirectionLabel } from "@/components/pool/pool-helpers";
import { formatCompactCurrency, formatCurrency, formatPercent } from "@/lib/formatters";
import type { CoinSummary } from "@/lib/types";
import type { PoolKey } from "@/lib/pool-meta";
import { RankBadge } from "@/components/pool/rank-badge";
import { ScoreBar } from "@/components/pool/score-bar";

const helper = createColumnHelper<CoinSummary>();

function createColumns(activePool: PoolKey) {
  const scoreLabel = activePool === "momentum" ? "冲浪分" : activePool === "trend" ? "趋势分" : activePool === "meanReversion" ? "逆势分" : "博弈分";

  return [
    helper.display({
      id: "rank",
      header: "排名",
      cell: ({ row }) => <RankBadge rank={row.original.rank} rankChange={row.original.rankChange} />,
    }),
    helper.accessor("baseAsset", {
      header: "币种",
      cell: ({ row }) => (
        <Link href={`/coin/${row.original.symbol}`} className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-indigo-500/14 text-indigo-200">
            {row.original.logoText}
          </div>
          <div>
            <div className="font-semibold text-slate-100">{row.original.baseAsset}</div>
            <div className="text-xs text-slate-400">{row.original.nameZh}</div>
          </div>
        </Link>
      ),
    }),
    helper.display({
      id: "poolScore",
      header: scoreLabel,
      cell: ({ row }) => <ScoreBar score={row.original.poolScores[activePool] ?? row.original.primaryScore ?? row.original.totalScore} label={scoreLabel} />,
    }),
    helper.accessor("price", {
      header: "价格 / 24h",
      cell: ({ getValue, row }) => (
        <div>
          <div className="font-mono text-slate-100">{formatCurrency(getValue(), getValue() < 5 ? 4 : 2)}</div>
          <div className={row.original.change24h >= 0 ? "text-up text-xs" : "text-down text-xs"}>{formatPercent(row.original.change24h)}</div>
        </div>
      ),
    }),
    helper.accessor("openInterest", {
      header: activePool === "trend" ? "Open Interest" : "仓位强度",
      cell: ({ getValue }) => {
        const value = getValue();
        return value !== null ? formatCompactCurrency(value) : "—";
      },
    }),
    helper.display({
      id: "direction",
      header: "方向",
      cell: ({ row }) => <span className="rounded-full bg-cyan-500/10 px-3 py-1 text-xs text-cyan-200">{getPoolDirectionLabel(row.original, activePool)}</span>,
    }),
    helper.display({
      id: "why",
      header: "入池理由",
      cell: ({ row }) => (
        <div className="flex flex-wrap gap-2">
          {row.original.reasonTags.slice(0, 2).map((tag) => (
            <span key={tag} className="rounded-full border border-cyan-400/14 bg-cyan-500/8 px-3 py-1 text-xs text-slate-200">
              {tag}
            </span>
          ))}
        </div>
      ),
    }),
  ];
}

export function RankingTable({ coins, activePool }: { coins: CoinSummary[]; activePool: PoolKey }) {
  const table = useReactTable({
    data: coins,
    columns: createColumns(activePool),
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <div className="panel hidden overflow-hidden rounded-[32px] lg:block">
      <table className="min-w-full divide-y divide-white/6 text-left text-sm text-slate-300">
        <thead className="bg-white/[0.02] text-xs uppercase tracking-[0.22em] text-slate-500">
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <th key={header.id} className="px-6 py-4 font-medium">
                  {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody className="divide-y divide-white/6">
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id} className="align-top transition hover:bg-white/[0.02]">
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id} className="px-6 py-5">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
