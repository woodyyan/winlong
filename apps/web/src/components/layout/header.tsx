"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, ChartCandlestick, LayoutGrid } from "lucide-react";
import clsx from "clsx";

const links = [
  { href: "/", label: "排行", icon: LayoutGrid },
  { href: "/status", label: "状态", icon: Activity },
];

export function Header() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-40 border-b border-white/6 bg-slate-950/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-[1280px] items-center justify-between px-4 py-3">
        <Link href="/" className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-indigo-500/14 text-indigo-300 glow-ring">
            <ChartCandlestick className="h-5 w-5" />
          </div>
          <div>
            <div className="text-sm uppercase tracking-[0.28em] text-slate-500">Winlong</div>
            <div className="text-lg font-semibold text-slate-100">AI 因子币种池</div>
          </div>
        </Link>

        <nav className="hidden items-center gap-2 md:flex">
          {links.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className={clsx(
                  "inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm transition",
                  active
                    ? "bg-indigo-500/14 text-indigo-200"
                    : "text-slate-400 hover:bg-white/5 hover:text-slate-100",
                )}
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
