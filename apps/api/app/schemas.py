from __future__ import annotations

from pydantic import BaseModel, Field


class CoinFactors(BaseModel):
    momentum: float
    liquidity: float
    derivatives: float
    community: float


class CoinSummary(BaseModel):
    symbol: str
    baseAsset: str
    name: str
    nameZh: str
    logoText: str
    price: float
    change24h: float
    volume24h: float
    marketCap: float
    totalScore: float
    rank: int
    rankChange: int
    factors: CoinFactors
    hasFutures: bool
    openInterest: float | None = None
    fundingRate: float | None = None
    longShortRatio: float | None = None
    primaryPool: str | None = None
    primaryScore: float | None = None
    poolScores: dict[str, float] = Field(default_factory=dict)
    reasonTags: list[str] = Field(default_factory=list)
    momentumDirection: str | None = None
    meanReversionDirection: str | None = None
    lsGameDirection: str | None = None
    tags: list[str]
    updatedAt: str


class PoolSummary(BaseModel):
    key: str
    name: str
    shortName: str
    description: str
    count: int
    avgScore: float
    leaderSymbol: str | None = None
    leaderScore: float | None = None
    leaderDirection: str | None = None


class WinlongListData(BaseModel):
    computedAt: str
    totalCoins: int
    returnedCount: int
    dataQuality: str
    pools: list[PoolSummary] = Field(default_factory=list)
    coins: list[CoinSummary]


class ListResponse(BaseModel):
    code: int
    message: str
    data: WinlongListData


class SubFactor(BaseModel):
    key: str
    name: str
    rawValue: float
    zScore: float
    weight: float
    contribution: float
    explanation: str


class FactorCategoryDetail(BaseModel):
    category: str
    label: str
    score: float
    subFactors: list[SubFactor]


class DerivativesPanel(BaseModel):
    hasFutures: bool
    openInterest: float | None = None
    fundingRate: float | None = None
    longShortRatio: float | None = None
    oiChange24h: float | None = None
    recentFundingRates: list[float] = Field(default_factory=list)


class MarketFeatureSnapshot(BaseModel):
    oiChange1h: float | None = None
    oiChange4h: float | None = None
    oiChange24h: float | None = None
    turnover24h: float | None = None
    oiToVolume: float | None = None
    oiToMarketcap: float | None = None
    corrBtc7d: float | None = None
    corrEth7d: float | None = None
    fundingRateMean24h: float | None = None
    fundingRateStd24h: float | None = None
    priceChange1h: float | None = None
    priceChange24h: float | None = None
    distanceToMa20: float | None = None
    priceVolatility7d: float | None = None
    longShortRatioStability: float | None = None
    oiStability7d: float | None = None
    liquidationToOi24h: float | None = None
    liquidationToVolume24h: float | None = None


class CoinDetailData(BaseModel):
    coin: CoinSummary
    factorDetails: list[FactorCategoryDetail]
    derivatives: DerivativesPanel
    marketFeatures: MarketFeatureSnapshot | None = None


class CoinDetailResponse(BaseModel):
    code: int
    message: str
    data: CoinDetailData


class HistoryPoint(BaseModel):
    timestamp: str
    score: float
    rank: int
    price: float


class CoinHistoryResponse(BaseModel):
    code: int
    message: str
    data: list[HistoryPoint]


class SourceStatusItem(BaseModel):
    source: str
    status: str
    latencyMs: int
    lastSuccessAt: str
    detail: str


class StatusLogItem(BaseModel):
    timestamp: str
    level: str
    message: str


class StatusOverview(BaseModel):
    computedAt: str
    lastScoreAt: str
    nextScoreAt: str
    refreshIntervalHours: int
    poolSize: int
    coinsWithFutures: int
    dataQuality: str
    databaseSizeMb: float
    uptime: str
    runtimeData: bool = False


class StatusData(BaseModel):
    overview: StatusOverview
    sources: list[SourceStatusItem]
    logs: list[StatusLogItem]


class StatusResponse(BaseModel):
    code: int
    message: str
    data: StatusData


class HealthResponse(BaseModel):
    ok: bool
    version: str
