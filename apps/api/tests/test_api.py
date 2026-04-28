from __future__ import annotations

from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.db import init_db, replace_runtime_dataset
from app.main import app
from app.services.market_sync_service import MarketSyncService
from app.services.pool_scoring_service import PoolScoringService
from app.services.winlong_service import WinlongService


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "test-winlong.db"
    init_db(db_path, force_reset=True)
    monkeypatch.setattr("app.main.service", WinlongService(db_path=db_path))
    with TestClient(app) as test_client:
        yield test_client


def test_health(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["version"] == "0.1.0"


def test_list_default_payload(client: TestClient):
    response = client.get("/api/winlong/list")
    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["returnedCount"] == 8
    assert payload["data"]["coins"][0]["symbol"] == "BTCUSDT"
    assert payload["data"]["coins"][0]["rank"] == 1

def test_list_includes_pool_summaries_and_direction_fields(client: TestClient):
    response = client.get("/api/winlong/list")
    assert response.status_code == 200
    data = response.json()["data"]

    assert len(data["pools"]) == 4
    assert data["pools"][0]["key"] == "momentum"
    assert data["pools"][0]["name"] == "冲浪池"
    assert sum(pool["count"] for pool in data["pools"]) >= data["totalCoins"]
    assert all(pool["count"] >= 0 for pool in data["pools"])
    assert any(pool["leaderSymbol"] is not None for pool in data["pools"])
    assert isinstance(data["pools"][0]["avgScore"], float)

    coin = data["coins"][0]
    assert coin["primaryPool"] in {"momentum", "trend", "meanReversion", "lsGame"}
    assert len(coin["poolMemberships"]) >= 1
    assert coin["primaryPool"] in coin["poolMemberships"]
    assert set(coin["poolScores"].keys()) == {"momentum", "trend", "meanReversion", "lsGame"}
    assert "momentumDirection" in coin
    assert "meanReversionDirection" in coin
    assert "lsGameDirection" in coin


def test_list_can_sort_by_score_desc(client: TestClient):
    response = client.get("/api/winlong/list?sort_by=score&order=desc&limit=3")
    assert response.status_code == 200
    coins = response.json()["data"]["coins"]
    scores = [coin["totalScore"] for coin in coins]
    assert scores == sorted(scores, reverse=True)


def test_list_filter_by_search_query(client: TestClient):
    response = client.get("/api/winlong/list?q=sol")
    assert response.status_code == 200
    coins = response.json()["data"]["coins"]
    assert len(coins) == 1
    assert coins[0]["symbol"] == "SOLUSDT"


def test_list_filter_by_tag(client: TestClient):
    response = client.get("/api/winlong/list?tag=ai")
    assert response.status_code == 200
    coins = response.json()["data"]["coins"]
    assert [coin["symbol"] for coin in coins] == ["TAOUSDT"]


def test_list_filter_by_score_threshold(client: TestClient):
    response = client.get("/api/winlong/list?min_score=85")
    assert response.status_code == 200
    coins = response.json()["data"]["coins"]
    assert all(coin["totalScore"] >= 85 for coin in coins)


def test_list_filter_by_offset(client: TestClient):
    response = client.get("/api/winlong/list?limit=2&offset=2")
    assert response.status_code == 200
    coins = response.json()["data"]["coins"]
    assert len(coins) == 2
    assert coins[0]["rank"] == 3


def test_pool_summaries_count_overlapping_memberships(client: TestClient):
    response = client.get("/api/winlong/list")
    assert response.status_code == 200
    data = response.json()["data"]

    counts = {pool["key"]: pool["count"] for pool in data["pools"]}
    membership_counts = {pool_key: 0 for pool_key in counts}
    for coin in data["coins"]:
        for pool_key in coin["poolMemberships"]:
            membership_counts[pool_key] += 1

    assert counts == membership_counts
    assert sum(counts.values()) >= data["totalCoins"]


def test_coin_detail_contains_factor_details(client: TestClient):
    response = client.get("/api/winlong/coins/BTCUSDT")
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["coin"]["symbol"] == "BTCUSDT"
    assert len(payload["factorDetails"]) == 4
    assert payload["derivatives"]["hasFutures"] is True
    assert len(payload["derivatives"]["recentFundingRates"]) == 6

def test_coin_detail_contains_pool_direction_fields(client: TestClient):
    response = client.get("/api/winlong/coins/ETHUSDT")
    assert response.status_code == 200
    coin = response.json()["data"]["coin"]

    assert coin["primaryPool"] in {"momentum", "trend", "meanReversion", "lsGame"}
    assert len(coin["poolMemberships"]) >= 1
    assert coin["primaryPool"] in coin["poolMemberships"]
    assert len(coin["reasonTags"]) >= 1
    assert set(coin["poolScores"].keys()) == {"momentum", "trend", "meanReversion", "lsGame"}
    assert "momentumDirection" in coin
    assert "meanReversionDirection" in coin
    assert "lsGameDirection" in coin


def test_coin_detail_for_missing_symbol_returns_404(client: TestClient):
    response = client.get("/api/winlong/coins/UNKNOWN")
    assert response.status_code == 404
    assert response.json()["code"] == 404


def test_coin_history_for_missing_symbol_returns_404(client: TestClient):
    response = client.get("/api/winlong/coins/UNKNOWN/history")
    assert response.status_code == 404
    assert response.json()["code"] == 404


def test_coin_history_respects_days_param(client: TestClient):
    response = client.get("/api/winlong/coins/ETHUSDT/history?days=7")
    assert response.status_code == 200
    history = response.json()["data"]
    assert len(history) == 7
    assert history[0]["timestamp"] < history[-1]["timestamp"]


def test_status_contains_sources_and_logs(client: TestClient):
    response = client.get("/api/winlong/status")
    assert response.status_code == 200
    status = response.json()["data"]
    assert status["overview"]["poolSize"] == 8
    assert status["overview"]["runtimeData"] is False
    assert len(status["sources"]) == 3
    assert len(status["logs"]) >= 1


def test_validation_error_shape(client: TestClient):
    response = client.get("/api/winlong/list?limit=999")
    assert response.status_code == 422
    payload = response.json()
    assert payload["code"] == 422
    assert payload["message"] == "invalid request"


def test_history_validation_error_shape(client: TestClient):
    response = client.get("/api/winlong/coins/BTCUSDT/history?days=999")
    assert response.status_code == 422
    payload = response.json()
    assert payload["code"] == 422
    assert payload["message"] == "invalid request"


@pytest.mark.anyio
async def test_market_sync_service_builds_runtime_dataset(monkeypatch: pytest.MonkeyPatch):
    service = MarketSyncService()

    async def fake_get_json(_, url: str, params=None):
        params = params or {}
        symbol = params.get("symbol")

        if url.endswith("/api/v3/exchangeInfo"):
            return {
                "symbols": [
                    {"baseAsset": "BTC", "quoteAsset": "USDT", "status": "TRADING"},
                    {"baseAsset": "ETH", "quoteAsset": "USDT", "status": "TRADING"},
                ]
            }
        if url.endswith("/api/v3/ticker/24hr"):
            return [
                {"symbol": "BTCUSDT", "lastPrice": "65000", "priceChangePercent": "3.5", "quoteVolume": "20000000000"},
                {"symbol": "ETHUSDT", "lastPrice": "3200", "priceChangePercent": "1.8", "quoteVolume": "9000000000"},
            ]
        if url.endswith("/fapi/v1/exchangeInfo"):
            return {
                "symbols": [
                    {"baseAsset": "BTC", "quoteAsset": "USDT", "contractType": "PERPETUAL", "status": "TRADING"},
                    {"baseAsset": "ETH", "quoteAsset": "USDT", "contractType": "PERPETUAL", "status": "TRADING"},
                ]
            }
        if url.endswith("/fapi/v1/ticker/24hr"):
            return [
                {"symbol": "BTCUSDT", "openInterest": "120000"},
                {"symbol": "ETHUSDT", "openInterest": "90000"},
            ]
        if url.endswith("/fapi/v1/premiumIndex"):
            return [
                {"symbol": "BTCUSDT", "markPrice": "65100", "lastFundingRate": "0.0001", "time": "1713705600000"},
                {"symbol": "ETHUSDT", "markPrice": "3210", "lastFundingRate": "0.00008", "time": "1713705600000"},
            ]
        if url.endswith("/coins/markets"):
            return [
                {"id": "bitcoin", "market_cap": 1200000000000},
                {"id": "ethereum", "market_cap": 400000000000},
            ]
        if url.endswith("/api/v3/klines"):
            if symbol == "BTCUSDT":
                return [[i, "0", "0", "0", str(60000 + i * 120), "0"] for i in range(168)]
            if symbol == "ETHUSDT":
                return [[i, "0", "0", "0", str(3000 + i * 8), "0"] for i in range(168)]
        if url.endswith("/futures/data/openInterestHist"):
            if symbol == "BTCUSDT":
                return [{"sumOpenInterestValue": str(7000000000 + i * 25000000)} for i in range(30)]
            if symbol == "ETHUSDT":
                return [{"sumOpenInterestValue": str(3000000000 + i * 10000000)} for i in range(30)]
        if url.endswith("/fapi/v1/fundingRate"):
            if symbol == "BTCUSDT":
                return [{"fundingRate": rate} for rate in ["0.00009", "0.0001", "0.00011", "0.0001"]]
            if symbol == "ETHUSDT":
                return [{"fundingRate": rate} for rate in ["0.00007", "0.00008", "0.00009", "0.00008"]]
        if url.endswith("/futures/data/globalLongShortAccountRatio"):
            if symbol == "BTCUSDT":
                return [{"longShortRatio": str(1.02 + i * 0.001)} for i in range(24)]
            if symbol == "ETHUSDT":
                return [{"longShortRatio": str(1.0 + i * 0.0008)} for i in range(24)]
        if url.endswith("/futures/data/topLongShortAccountRatio"):
            if symbol == "BTCUSDT":
                return [{"longShortRatio": str(1.08 + i * 0.001)} for i in range(24)]
            if symbol == "ETHUSDT":
                return [{"longShortRatio": str(1.03 + i * 0.0008)} for i in range(24)]
        if url.endswith("/futures/data/topLongShortPositionRatio"):
            if symbol == "BTCUSDT":
                return [{"longShortRatio": str(1.12 + i * 0.001)} for i in range(24)]
            if symbol == "ETHUSDT":
                return [{"longShortRatio": str(1.04 + i * 0.0008)} for i in range(24)]
        raise AssertionError(f"unexpected url: {url}")

    monkeypatch.setattr(service, "_get_json", fake_get_json)

    payload, snapshots, features, pool_scores = await service.build_runtime_dataset()

    assert payload["overview"]["poolSize"] == 2
    assert payload["coins"][0]["symbol"] == "BTCUSDT"
    assert payload["coins"][0]["marketCap"] > 0
    assert payload["coins"][0]["primaryPool"] in {"momentum", "trend", "meanReversion", "lsGame"}
    assert len(payload["coins"][0]["poolMemberships"]) >= 1
    assert payload["coins"][0]["primaryPool"] in payload["coins"][0]["poolMemberships"]
    assert set(payload["coins"][0]["poolScores"].keys()) == {"momentum", "trend", "meanReversion", "lsGame"}
    assert len(payload["coins"][0]["reasonTags"]) == 3
    assert len(payload["factorRows"]) > 0
    assert len(snapshots) == 2
    assert len(features) == 2
    assert len(pool_scores) == 2
    assert features[0]["featureTime"] == payload["coins"][0]["updatedAt"]
    assert pool_scores[0]["primaryPool"] in {"momentum", "trend", "meanReversion", "lsGame"}
    assert features[0]["corrBtc7d"] >= 0.9
    assert features[0]["fundingRateStd24h"] >= 0
    assert features[0]["longShortRatioStability"] >= 0


def test_replace_runtime_dataset_sets_runtime_status(tmp_path: Path):
    db_path = tmp_path / "runtime.db"
    init_db(db_path, force_reset=True)
    service = MarketSyncService()

    rows = [
        {
            "symbol": "BTCUSDT",
            "baseAsset": "BTC",
            "name": "Bitcoin",
            "nameZh": "比特币",
            "logoText": "BTC",
            "price": 65000.0,
            "change24h": 3.5,
            "volume24h": 20000000000.0,
            "marketCap": 1200000000000.0,
            "openInterest": 7812000000.0,
            "fundingRate": 0.0001,
            "predictedFundingRate": 0.0001,
            "longShortRatio": 1.18,
            "hasFutures": True,
            "tags": ["core"],
            "snapshotTime": "2026-04-26T10:00:00Z",
            "updatedAt": "2026-04-26T10:00:00Z",
        }
    ]

    payload, features, pool_scores = service._build_payload(rows)  # noqa: SLF001
    snapshots = service._build_snapshots(rows)  # noqa: SLF001
    replace_runtime_dataset(payload, snapshots=snapshots, features=features, pool_scores=pool_scores, db_path=db_path)

    runtime_client = WinlongService(db_path=db_path)
    status = runtime_client.get_status()["data"]["overview"]
    coin = runtime_client.list_coins(limit=1, offset=0, min_score=0, sort_by="rank", order="asc")["data"]["coins"][0]
    detail = runtime_client.get_coin_detail("BTCUSDT")["data"]

    assert status["runtimeData"] is True
    assert status["poolSize"] == 1
    assert coin["primaryPool"] in {"momentum", "trend", "meanReversion", "lsGame"}
    assert len(coin["poolMemberships"]) >= 1
    assert coin["primaryPool"] in coin["poolMemberships"]
    assert set(coin["poolScores"].keys()) == {"momentum", "trend", "meanReversion", "lsGame"}
    assert len(coin["reasonTags"]) == 3
    assert detail["marketFeatures"] is not None
    assert detail["marketFeatures"]["turnover24h"] is not None


def test_runtime_payload_survives_missing_optional_metrics(tmp_path: Path):
    db_path = tmp_path / "runtime-partial.db"
    init_db(db_path, force_reset=True)
    service = MarketSyncService()

    rows = [
        {
            "symbol": "ETHUSDT",
            "baseAsset": "ETH",
            "name": "Ethereum",
            "nameZh": "以太坊",
            "logoText": "ETH",
            "price": 3200.0,
            "change24h": -2.2,
            "volume24h": 9000000000.0,
            "marketCap": 400000000000.0,
            "openInterest": 4800000000.0,
            "fundingRate": None,
            "predictedFundingRate": None,
            "longShortRatio": None,
            "hasFutures": True,
            "tags": ["smart-contract"],
            "snapshotTime": "2026-04-26T10:00:00Z",
            "updatedAt": "2026-04-26T10:00:00Z",
        }
    ]

    payload, features, pool_scores = service._build_payload(rows)  # noqa: SLF001
    snapshots = service._build_snapshots(rows)  # noqa: SLF001
    replace_runtime_dataset(payload, snapshots=snapshots, features=features, pool_scores=pool_scores, db_path=db_path)

    runtime_client = WinlongService(db_path=db_path)
    detail = runtime_client.get_coin_detail("ETHUSDT")["data"]

    assert detail["coin"]["primaryPool"] in {"momentum", "trend", "meanReversion", "lsGame"}
    assert detail["coin"]["primaryPool"] in detail["coin"]["poolMemberships"]
    assert detail["coin"]["poolScores"][detail["coin"]["primaryPool"]] == detail["coin"]["primaryScore"]
    assert detail["marketFeatures"]["fundingRateMean24h"] == 0.0
    assert detail["marketFeatures"]["longShortRatioStability"] == 0.0


def test_pool_scoring_service_assigns_expected_primary_pool():
    service = PoolScoringService()
    rows = [
        {
            "symbol": "MOMUSDT",
            "updatedAt": "2026-04-27T00:00:00Z",
            "marketCap": 300000000,
            "volume24h": 180000000,
            "openInterest": 90000000,
            "change24h": 12.0,
            "priceChange1h": 2.8,
            "oiChange1h": 5.0,
            "oiChange4h": 18.0,
            "oiChange24h": 42.0,
            "fundingRate": 0.00024,
            "fundingRateMean24h": 0.00022,
            "fundingRateStd24h": 0.00005,
            "predictedFundingRate": 0.00026,
            "longShortRatio": 1.08,
            "longShortRatioMean24h": 1.05,
            "longShortRatioStability": 0.03,
            "oiStability7d": 2.0,
            "corrBtc7d": 0.58,
            "corrEth7d": 0.56,
            "distanceToMa20": 8.0,
            "priceVolatility7d": 6.0,
            "liquidationToOi24h": 0.35,
            "liquidationToVolume24h": 0.08,
            "topTraderSpread": 0.12,
            "crowdingScore": 0.2,
        },
        {
            "symbol": "TRDUSDT",
            "updatedAt": "2026-04-27T00:00:00Z",
            "marketCap": 900000000,
            "volume24h": 160000000,
            "openInterest": 180000000,
            "change24h": 4.0,
            "priceChange1h": 0.4,
            "oiChange1h": 0.8,
            "oiChange4h": 3.0,
            "oiChange24h": 14.0,
            "fundingRate": 0.00009,
            "fundingRateMean24h": 0.0001,
            "fundingRateStd24h": 0.00001,
            "predictedFundingRate": 0.00009,
            "longShortRatio": 1.01,
            "longShortRatioMean24h": 1.01,
            "longShortRatioStability": 0.01,
            "oiStability7d": 0.6,
            "corrBtc7d": 0.72,
            "corrEth7d": 0.71,
            "distanceToMa20": 2.2,
            "priceVolatility7d": 2.5,
            "liquidationToOi24h": 0.04,
            "liquidationToVolume24h": 0.01,
            "topTraderSpread": 0.02,
            "crowdingScore": 0.03,
        },
        {
            "symbol": "REVUSDT",
            "updatedAt": "2026-04-27T00:00:00Z",
            "marketCap": 250000000,
            "volume24h": 95000000,
            "openInterest": 45000000,
            "change24h": -13.0,
            "priceChange1h": -3.2,
            "oiChange1h": -6.0,
            "oiChange4h": -12.0,
            "oiChange24h": -28.0,
            "fundingRate": -0.00032,
            "fundingRateMean24h": -0.00028,
            "fundingRateStd24h": 0.00007,
            "predictedFundingRate": -0.00031,
            "longShortRatio": 0.91,
            "longShortRatioMean24h": 0.93,
            "longShortRatioStability": 0.05,
            "oiStability7d": 3.8,
            "corrBtc7d": 0.49,
            "corrEth7d": 0.52,
            "distanceToMa20": -12.0,
            "priceVolatility7d": 8.0,
            "liquidationToOi24h": 0.42,
            "liquidationToVolume24h": 0.11,
            "topTraderSpread": 0.1,
            "crowdingScore": 0.23,
        },
        {
            "symbol": "LSGUSDT",
            "updatedAt": "2026-04-27T00:00:00Z",
            "marketCap": 220000000,
            "volume24h": 70000000,
            "openInterest": 120000000,
            "change24h": 1.5,
            "priceChange1h": 0.1,
            "oiChange1h": 0.6,
            "oiChange4h": 2.0,
            "oiChange24h": 6.0,
            "fundingRate": -0.00022,
            "fundingRateMean24h": -0.0002,
            "fundingRateStd24h": 0.00003,
            "predictedFundingRate": -0.00024,
            "longShortRatio": 0.84,
            "longShortRatioMean24h": 0.86,
            "longShortRatioStability": 0.12,
            "oiStability7d": 1.5,
            "corrBtc7d": 0.44,
            "corrEth7d": 0.41,
            "distanceToMa20": 1.0,
            "priceVolatility7d": 3.2,
            "liquidationToOi24h": 0.09,
            "liquidationToVolume24h": 0.03,
            "topTraderSpread": 0.24,
            "crowdingScore": 0.4,
        },
    ]

    _, features, pool_scores = service.build_features_and_scores(rows)

    primary_map = {row["symbol"]: row["primaryPool"] for row in pool_scores}
    reason_map = {row["symbol"]: row["reasonTags"] for row in pool_scores}
    feature_map = {row["symbol"]: row for row in features}
    membership_map = {row["symbol"]: row["poolMemberships"] for row in features}

    assert primary_map == {
        "MOMUSDT": "momentum",
        "TRDUSDT": "trend",
        "REVUSDT": "meanReversion",
        "LSGUSDT": "lsGame",
    }
    assert feature_map["TRDUSDT"]["trendScore"] > feature_map["TRDUSDT"]["momentumScore"]
    assert membership_map["MOMUSDT"][0] == "momentum"
    assert "trend" in membership_map["MOMUSDT"]
    assert "trend" in membership_map["TRDUSDT"]
    assert feature_map["REVUSDT"]["meanReversionDirection"] == "rebound-long"
    assert feature_map["LSGUSDT"]["lsGameDirection"] == "short-squeeze candidate"
    assert len(reason_map["MOMUSDT"]) == 3


def test_merge_market_rows_allows_non_registry_symbol_with_market_cap():
    service = MarketSyncService()
    rows = service._merge_market_rows(  # noqa: SLF001
        spot_symbols={"BTC", "FART"},
        futures_symbols={"BTC", "FART"},
        spot_tickers=[
            {"symbol": "BTCUSDT", "lastPrice": "65000", "priceChangePercent": "3.5", "quoteVolume": "20000000000"},
            {"symbol": "FARTUSDT", "lastPrice": "1.2", "priceChangePercent": "12.0", "quoteVolume": "150000000"},
        ],
        futures_tickers=[
            {"symbol": "BTCUSDT", "openInterest": "120000"},
            {"symbol": "FARTUSDT", "openInterest": "2500000"},
        ],
        premium_index=[
            {"symbol": "BTCUSDT", "markPrice": "65100", "lastFundingRate": "0.0001", "time": "1713705600000"},
            {"symbol": "FARTUSDT", "markPrice": "1.21", "lastFundingRate": "0.0004", "time": "1713705600000"},
        ],
        market_caps={
            "BTC": {"marketCap": 1200000000000.0, "name": "Bitcoin", "coingeckoId": "bitcoin"},
            "FART": {"marketCap": 25000000.0, "name": "Fartcoin", "coingeckoId": "fartcoin"},
        },
    )

    fart_row = next(row for row in rows if row["symbol"] == "FARTUSDT")
    assert fart_row["name"] == "Fartcoin"
    assert fart_row["nameZh"] == "Fartcoin"
    assert fart_row["logoText"] == "FART"
    assert fart_row["tags"] == []
    assert fart_row["marketCap"] == 25000000.0


def test_merge_market_rows_uses_top_100_by_quote_volume():
    service = MarketSyncService()
    spot_symbols = {f"C{index:03d}" for index in range(105)}
    futures_symbols = set(spot_symbols)
    spot_tickers = []
    futures_tickers = []
    premium_index = []
    market_caps = {}

    for index in range(105):
        base_asset = f"C{index:03d}"
        symbol = f"{base_asset}USDT"
        spot_tickers.append(
            {"symbol": symbol, "lastPrice": "1.0", "priceChangePercent": "1.0", "quoteVolume": str(1000000 + index)}
        )
        futures_tickers.append({"symbol": symbol, "openInterest": "1000"})
        premium_index.append({"symbol": symbol, "markPrice": "1.0", "lastFundingRate": "0.0001", "time": "1713705600000"})
        market_caps[base_asset] = {"marketCap": 20000000.0, "name": base_asset, "coingeckoId": base_asset.lower()}

    rows = service._merge_market_rows(  # noqa: SLF001
        spot_symbols=spot_symbols,
        futures_symbols=futures_symbols,
        spot_tickers=spot_tickers,
        futures_tickers=futures_tickers,
        premium_index=premium_index,
        market_caps=market_caps,
    )

    assert len(rows) == 100
    assert rows[0]["symbol"] == "C104USDT"
    assert rows[-1]["symbol"] == "C005USDT"


def test_pool_scoring_service_handles_single_row_universe():
    service = PoolScoringService()
    rows = [
        {
            "symbol": "ONLYUSDT",
            "updatedAt": "2026-04-27T00:00:00Z",
            "marketCap": 100000000,
            "volume24h": 50000000,
            "openInterest": 20000000,
            "change24h": 5.0,
            "fundingRate": 0.0001,
            "predictedFundingRate": 0.0001,
            "longShortRatio": 1.0,
        }
    ]

    scored_rows, features, pool_scores = service.build_features_and_scores(rows)

    assert len(scored_rows) == 1
    assert len(features) == 1
    assert len(pool_scores) == 1
    assert scored_rows[0]["primaryPool"] in {"momentum", "trend", "meanReversion", "lsGame"}
    assert scored_rows[0]["primaryPool"] in scored_rows[0]["poolMemberships"]
    assert all(0 <= score <= 100 for score in scored_rows[0]["poolScores"].values())
    assert len(scored_rows[0]["reasonTags"]) == 3


@pytest.mark.anyio
async def test_market_sync_service_symbol_metric_fallbacks_on_partial_failure(monkeypatch: pytest.MonkeyPatch):
    service = MarketSyncService()
    row = {
        "symbol": "BTCUSDT",
        "baseAsset": "BTC",
        "change24h": 3.5,
        "volume24h": 20000000000.0,
        "marketCap": 1200000000000.0,
        "openInterest": 7800000000.0,
        "fundingRate": 0.0001,
        "predictedFundingRate": 0.0001,
        "longShortRatio": 1.12,
    }

    async def fake_close_series(*args, **kwargs):
        return [60000 + i * 100 for i in range(168)]

    async def fake_oi_hist(*args, **kwargs):
        return [7000000000 + i * 10000000 for i in range(30)]

    async def fake_funding(*args, **kwargs):
        raise RuntimeError("funding endpoint unavailable")

    async def fake_global_ratio(*args, **kwargs):
        return [1.0 + i * 0.001 for i in range(24)]

    async def fake_top_account(*args, **kwargs):
        return [1.05 + i * 0.001 for i in range(24)]

    async def fake_top_position(*args, **kwargs):
        return [1.08 + i * 0.001 for i in range(24)]

    monkeypatch.setattr(service, "_fetch_close_series", fake_close_series)
    monkeypatch.setattr(service, "_fetch_open_interest_hist", fake_oi_hist)
    monkeypatch.setattr(service, "_fetch_funding_rate_series", fake_funding)
    monkeypatch.setattr(service, "_fetch_long_short_ratio_series", fake_global_ratio)

    async def fake_ratio_router(client, symbol, endpoint, **kwargs):
        if endpoint == "globalLongShortAccountRatio":
            return await fake_global_ratio()
        if endpoint == "topLongShortAccountRatio":
            return await fake_top_account()
        return await fake_top_position()

    monkeypatch.setattr(service, "_fetch_long_short_ratio_series", fake_ratio_router)

    metrics = await service._fetch_symbol_detail_metrics(  # noqa: SLF001
        None,
        row,
        {"BTCUSDT": [60000 + i * 100 for i in range(168)], "ETHUSDT": [3000 + i * 10 for i in range(168)]},
    )

    assert metrics["fundingRateMean24h"] == row["fundingRate"]
    assert metrics["predictedFundingRate"] == row["predictedFundingRate"]
    assert metrics["corrBtc7d"] >= 0.9
    assert metrics["topTraderSpread"] > 0
