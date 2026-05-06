import type {
  CoinDetailResponse,
  CoinHistoryResponse,
  StatusResponse,
  WinlongListResponse,
} from "@/lib/types";

function getApiBaseUrl() {
  return typeof window === "undefined" ? process.env.API_BASE_URL ?? "http://127.0.0.1:8001" : "";
}

async function fetchJson<T>(path: string, revalidate = 60): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    next: { revalidate },
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${path}`);
  }

  return response.json() as Promise<T>;
}

export async function getWinlongList() {
  return fetchJson<WinlongListResponse>("/api/winlong/list?sort_by=score&order=desc&limit=150", 60);
}

export async function getCoinDetail(symbol: string) {
  return fetchJson<CoinDetailResponse>(`/api/winlong/coins/${symbol}`, 60);
}

export async function getCoinHistory(symbol: string) {
  return fetchJson<CoinHistoryResponse>(`/api/winlong/coins/${symbol}/history?days=30`, 60);
}

export async function getStatus() {
  return fetchJson<StatusResponse>("/api/winlong/status", 30);
}

export async function clientFetcher<T>(path: string): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed: ${path}`);
  }
  return response.json() as Promise<T>;
}
