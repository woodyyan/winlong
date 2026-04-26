import { getScoreTone } from "@/lib/formatters";

const toneMap = {
  excellent: "bg-emerald-500",
  good: "bg-sky-500",
  average: "bg-amber-500",
  poor: "bg-rose-500",
};

export function ScoreBar({ score }: { score: number }) {
  const tone = getScoreTone(score);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs text-slate-400">
        <span>AI 评分</span>
        <span className="font-mono text-sm font-semibold text-slate-100">{score.toFixed(1)}</span>
      </div>
      <div className="score-track h-2 overflow-hidden rounded-full">
        <div className={`h-full rounded-full ${toneMap[tone]}`} style={{ width: `${score}%` }} />
      </div>
    </div>
  );
}
