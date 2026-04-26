export type FactorName = "momentum" | "liquidity" | "derivatives" | "community";

export interface CoinFactors {
  momentum: number;
  liquidity: number;
  derivatives: number;
  community: number;
}

export interface CoinSummary {
  symbol: string;
  baseAsset: string;
  name: string;
  nameZh: string;
  logoText: string;
  price: number;
  change24h: number;
  volume24h: number;
  marketCap: number;
  totalScore: number;
  rank: number;
  rankChange: number;
  factors: CoinFactors;
  hasFutures: boolean;
  openInterest: number | null;
  fundingRate: number | null;
  longShortRatio: number | null;
  tags: string[];
  updatedAt: string;
}

export interface SubFactor {
  key: string;
  name: string;
  rawValue: number;
  zScore: number;
  weight: number;
  contribution: number;
  explanation: string;
}

export interface FactorCategoryDetail {
  category: FactorName;
  label: string;
  score: number;
  subFactors: SubFactor[];
}

export interface DerivativesPanel {
  hasFutures: boolean;
  openInterest: number | null;
  fundingRate: number | null;
  longShortRatio: number | null;
  oiChange24h: number | null;
  recentFundingRates: number[];
}

export interface WinlongListData {
  computedAt: string;
  totalCoins: number;
  returnedCount: number;
  dataQuality: string;
  coins: CoinSummary[];
}

export interface WinlongListResponse {
  code: number;
  message: string;
  data: WinlongListData;
}

export interface CoinDetailResponse {
  code: number;
  message: string;
  data: {
    coin: CoinSummary;
    factorDetails: FactorCategoryDetail[];
    derivatives: DerivativesPanel;
  };
}

export interface HistoryPoint {
  timestamp: string;
  score: number;
  rank: number;
  price: number;
}

export interface CoinHistoryResponse {
  code: number;
  message: string;
  data: HistoryPoint[];
}

export interface SourceStatusItem {
  source: string;
  status: string;
  latencyMs: number;
  lastSuccessAt: string;
  detail: string;
}

export interface StatusLogItem {
  timestamp: string;
  level: string;
  message: string;
}

export interface StatusOverview {
  computedAt: string;
  lastScoreAt: string;
  nextScoreAt: string;
  refreshIntervalHours: number;
  poolSize: number;
  coinsWithFutures: number;
  dataQuality: string;
  databaseSizeMb: number;
  uptime: string;
}

export interface StatusResponse {
  code: number;
  message: string;
  data: {
    overview: StatusOverview;
    sources: SourceStatusItem[];
    logs: StatusLogItem[];
  };
}
