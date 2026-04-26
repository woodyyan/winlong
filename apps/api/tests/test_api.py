from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.db import init_db
from app.main import app
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
    assert len(status["sources"]) == 3
    assert len(status["logs"]) >= 1


def test_validation_error_shape(client: TestClient):
    response = client.get("/api/winlong/list?limit=999")
    assert response.status_code == 422
    payload = response.json()
    assert payload["code"] == 422
    assert payload["message"] == "invalid request"
