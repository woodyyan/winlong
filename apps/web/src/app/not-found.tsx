import Link from "next/link";

export default function NotFound() {
  return (
    <main className="page-shell flex min-h-[70vh] items-center justify-center">
      <section className="panel max-w-xl rounded-3xl p-8 text-center">
        <p className="text-sm uppercase tracking-[0.3em] text-slate-500">404</p>
        <h1 className="mt-3 text-3xl font-semibold">这个币种暂时不在榜单里</h1>
        <p className="mt-4 text-slate-400">可能还没进入当前评分池，或者你输入的交易对不正确。</p>
        <Link
          href="/"
          className="mt-6 inline-flex rounded-full bg-indigo-500/14 px-5 py-3 text-sm text-indigo-200"
        >
          返回排行榜
        </Link>
      </section>
    </main>
  );
}
