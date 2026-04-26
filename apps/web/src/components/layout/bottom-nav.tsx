"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, Home } from "lucide-react";
import clsx from "clsx";

const links = [
  { href: "/", label: "排行", icon: Home },
  { href: "/status", label: "状态", icon: Activity },
];

export function BottomNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed inset-x-0 bottom-0 z-40 border-t border-white/6 bg-slate-950/90 px-4 py-3 backdrop-blur md:hidden">
      <div className="mx-auto flex max-w-md items-center justify-around rounded-3xl border border-white/6 bg-slate-900/80 px-2 py-2">
        {links.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={clsx(
                "flex min-w-24 flex-col items-center gap-1 rounded-2xl px-4 py-2 text-xs",
                active ? "bg-indigo-500/14 text-indigo-200" : "text-slate-500",
              )}
            >
              <Icon className="h-4 w-4" />
              <span>{label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
