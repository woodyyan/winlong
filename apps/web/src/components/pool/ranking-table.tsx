"use client";

import Link from "next/link";
import { createColumnHelper, flexRender, getCoreRowModel, useReactTable } from "@tanstack/react-table";

import { formatCompactCurrency, formatCurrency, formatPercent } from "@/lib/formatters";
import type { CoinSummary } from "@/lib/types";
import { FactorMiniBars } from "@/components/pool/factor-mini-bars";
import { RankBadge } from "@/components/pool/rank-badge";
import { ScoreBar } from "@/components/pool/score-bar";

const helper = createColumnHelper<CoinSummary>();

const columns = [
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
  helper.accessor("price", {
    header: "价格",
    cell: ({ getValue, row }) => (
      <div>
        <div className="font-mono text-slate-100">{formatCurrency(getValue(), getValue() < 5 ? 4 : 2)}</div>
        <div className={row.original.change24h >= 0 ? "text-up text-xs" : "text-down text-xs"}>
          {formatPercent(row.original.change24h)}
        </div>
      </div>
    ),
  }),
  helper.accessor("totalScore", {
    header: "评分",
    cell: ({ getValue }) => <ScoreBar score={getValue()} />,
  }),
  helper.accessor("factors", {
    header: "因子",
    cell: ({ getValue }) => <FactorMiniBars factors={getValue()} />,
  }),
  helper.accessor("volume24h", {
    header: "24h 成交量",
    cell: ({ getValue }) => formatCompactCurrency(getValue()),
  }),
];

export function RankingTable({ coins }: { coins: CoinSummary[] }) {
  const table = useReactTable({
    data: coins,
    columns,
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
