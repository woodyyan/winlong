import type { Metadata } from "next";

import "@/app/globals.css";
import { BottomNav } from "@/components/layout/bottom-nav";
import { Header } from "@/components/layout/header";

export const metadata: Metadata = {
  title: "Winlong · AI 因子币种池",
  description: "基于多因子评分的加密货币智能排行榜网站",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body>
        <Header />
        {children}
        <BottomNav />
      </body>
    </html>
  );
}
