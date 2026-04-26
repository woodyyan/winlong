import numeral from "numeral";

export function formatCurrency(value: number, digits = 2): string {
  if (Math.abs(value) >= 1000) {
    return `$${numeral(value).format(`0,0.${"0".repeat(digits)}`)}`;
  }
  return `$${value.toFixed(digits)}`;
}

export function formatCompactCurrency(value: number): string {
  return `$${numeral(value).format("0.00a").toUpperCase()}`;
}

export function formatPercent(value: number): string {
  const prefix = value > 0 ? "+" : "";
  return `${prefix}${value.toFixed(2)}%`;
}

export function formatSignedCurrency(value: number): string {
  const prefix = value > 0 ? "+" : "";
  return `${prefix}${formatCurrency(value)}`;
}

export function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export function formatTimeAgo(value: string): string {
  const diff = Date.now() - new Date(value).getTime();
  const minutes = Math.max(1, Math.floor(diff / 60000));
  if (minutes < 60) {
    return `${minutes} 分钟前`;
  }
  const hours = Math.floor(minutes / 60);
  if (hours < 24) {
    return `${hours} 小时前`;
  }
  const days = Math.floor(hours / 24);
  return `${days} 天前`;
}

export function getScoreTone(score: number): "excellent" | "good" | "average" | "poor" {
  if (score >= 80) return "excellent";
  if (score >= 60) return "good";
  if (score >= 40) return "average";
  return "poor";
}
