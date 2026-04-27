from __future__ import annotations

from pydantic import BaseModel


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
    tags: list[str]
    updatedAt: str


class WinlongListData(BaseModel):
    computedAt: str
    totalCoins: int
    returnedCount: int
    dataQuality: str
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
    recentFundingRates: list[float] = []


class CoinDetailData(BaseModel):
    coin: CoinSummary
    factorDetails: list[FactorCategoryDetail]
    derivatives: DerivativesPanel


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
