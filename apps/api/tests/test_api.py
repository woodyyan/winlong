from __future__ import annotations

from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.db import init_db
from app.main import app
from app.services.market_sync_service import MarketSyncService
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


def test_coin_detail_contains_factor_details(client: TestClient):
    response = client.get("/api/winlong/coins/BTCUSDT")
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["coin"]["symbol"] == "BTCUSDT"
    assert len(payload["factorDetails"]) == 4
    assert payload["derivatives"]["hasFutures"] is True
    assert len(payload["derivatives"]["recentFundingRates"]) == 6


def test_coin_detail_for_missing_symbol_returns_404(client: TestClient):
    response = client.get("/api/winlong/coins/UNKNOWN")
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


@pytest.mark.anyio
async def test_market_sync_service_builds_runtime_dataset(monkeypatch: pytest.MonkeyPatch):
    service = MarketSyncService()

    async def fake_get_json(_, url: str, params=None):
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
        raise AssertionError(f"unexpected url: {url}")

    monkeypatch.setattr(service, "_get_json", fake_get_json)

    payload, snapshots = await service.build_runtime_dataset()

    assert payload["overview"]["poolSize"] == 2
    assert payload["coins"][0]["symbol"] == "BTCUSDT"
    assert payload["coins"][0]["marketCap"] > 0
    assert len(payload["factorRows"]) > 0
    assert len(snapshots) == 2


def test_replace_runtime_dataset_sets_runtime_status(tmp_path: Path):
    from app.db import replace_runtime_dataset

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

    payload = service._build_payload(rows)  # noqa: SLF001
    snapshots = service._build_snapshots(rows)  # noqa: SLF001
    replace_runtime_dataset(payload, snapshots=snapshots, db_path=db_path)

    runtime_client = WinlongService(db_path=db_path)
    status = runtime_client.get_status()["data"]["overview"]
    assert status["runtimeData"] is True
    assert status["poolSize"] == 1
