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
  primaryPool?: "momentum" | "trend" | "meanReversion" | "lsGame" | null;
  primaryScore?: number | null;
  poolScores: Partial<Record<"momentum" | "trend" | "meanReversion" | "lsGame", number>>;
  reasonTags: string[];
  momentumDirection?: string | null;
  meanReversionDirection?: string | null;
  lsGameDirection?: string | null;
  tags: string[];
  updatedAt: string;
}

export interface PoolSummary {
  key: "momentum" | "trend" | "meanReversion" | "lsGame";
  name: string;
  shortName: string;
  description: string;
  count: number;
  avgScore: number;
  leaderSymbol: string | null;
  leaderScore: number | null;
  leaderDirection: string | null;
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

export interface MarketFeatureSnapshot {
  oiChange1h: number | null;
  oiChange4h: number | null;
  oiChange24h: number | null;
  turnover24h: number | null;
  oiToVolume: number | null;
  oiToMarketcap: number | null;
  corrBtc7d: number | null;
  corrEth7d: number | null;
  fundingRateMean24h: number | null;
  fundingRateStd24h: number | null;
  priceChange1h: number | null;
  priceChange24h: number | null;
  distanceToMa20: number | null;
  priceVolatility7d: number | null;
  longShortRatioStability: number | null;
  oiStability7d: number | null;
  liquidationToOi24h: number | null;
  liquidationToVolume24h: number | null;
}

export interface WinlongListData {
  computedAt: string;
  totalCoins: number;
  returnedCount: number;
  dataQuality: string;
  pools: PoolSummary[];
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
    marketFeatures: MarketFeatureSnapshot | null;
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
  runtimeData: boolean;
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
