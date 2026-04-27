from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from app.config import settings
from app.data.seed_payload import build_seed_payload


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS coins (
    symbol TEXT PRIMARY KEY,
    base_asset TEXT NOT NULL,
    name TEXT NOT NULL,
    name_zh TEXT NOT NULL,
    logo_text TEXT NOT NULL,
    price REAL NOT NULL,
    change_24h REAL NOT NULL,
    volume_24h REAL NOT NULL,
    market_cap REAL NOT NULL,
    total_score REAL NOT NULL,
    rank INTEGER NOT NULL,
    rank_change INTEGER NOT NULL,
    momentum REAL NOT NULL,
    liquidity REAL NOT NULL,
    derivatives REAL NOT NULL,
    community REAL NOT NULL,
    has_futures INTEGER NOT NULL,
    open_interest REAL,
    funding_rate REAL,
    long_short_ratio REAL,
    oi_change_24h REAL,
    recent_funding_rates TEXT NOT NULL,
    tags TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS factor_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    category TEXT NOT NULL,
    label TEXT NOT NULL,
    score REAL NOT NULL,
    subfactor_key TEXT NOT NULL,
    subfactor_name TEXT NOT NULL,
    raw_value REAL NOT NULL,
    z_score REAL NOT NULL,
    weight REAL NOT NULL,
    contribution REAL NOT NULL,
    explanation TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS history_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    score REAL NOT NULL,
    rank INTEGER NOT NULL,
    price REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS source_status (
    source TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    latency_ms INTEGER NOT NULL,
    last_success_at TEXT NOT NULL,
    detail TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    level TEXT NOT NULL,
    message TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS status_overview (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    computed_at TEXT NOT NULL,
    last_score_at TEXT NOT NULL,
    next_score_at TEXT NOT NULL,
    refresh_interval_hours INTEGER NOT NULL,
    pool_size INTEGER NOT NULL,
    coins_with_futures INTEGER NOT NULL,
    data_quality TEXT NOT NULL,
    uptime TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS market_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    snapshot_time TEXT NOT NULL,
    price REAL NOT NULL,
    price_change_24h REAL NOT NULL,
    quote_volume_24h REAL NOT NULL,
    market_cap REAL NOT NULL,
    open_interest REAL,
    funding_rate REAL,
    predicted_funding_rate REAL,
    global_long_short_ratio REAL,
    top_long_short_ratio REAL,
    top_position_ratio REAL,
    liquidation_notional_24h REAL,
    source TEXT NOT NULL,
    tags TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_market_snapshots_symbol_time
ON market_snapshots(symbol, snapshot_time DESC);

CREATE TABLE IF NOT EXISTS market_features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    feature_time TEXT NOT NULL,
    oi_change_1h REAL,
    oi_change_4h REAL,
    oi_change_24h REAL,
    turnover_24h REAL,
    oi_to_volume REAL,
    oi_to_marketcap REAL,
    corr_btc_7d REAL,
    corr_eth_7d REAL,
    funding_rate_mean_24h REAL,
    funding_rate_std_24h REAL,
    price_change_1h REAL,
    price_change_24h REAL,
    distance_to_ma20 REAL,
    price_volatility_7d REAL,
    long_short_ratio_stability REAL,
    oi_stability_7d REAL,
    liquidation_to_oi_24h REAL,
    liquidation_to_volume_24h REAL
);

CREATE INDEX IF NOT EXISTS idx_market_features_symbol_time
ON market_features(symbol, feature_time DESC);

CREATE TABLE IF NOT EXISTS pool_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    score_time TEXT NOT NULL,
    momentum_score REAL NOT NULL,
    trend_score REAL NOT NULL,
    mean_reversion_score REAL NOT NULL,
    ls_game_score REAL NOT NULL,
    momentum_direction TEXT,
    mean_reversion_direction TEXT,
    ls_game_direction TEXT,
    primary_pool TEXT NOT NULL,
    primary_score REAL NOT NULL,
    reason_tags TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_pool_scores_symbol_time
ON pool_scores(symbol, score_time DESC);
"""


def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    target = db_path or settings.db_path
    _ensure_parent_dir(target)
    conn = sqlite3.connect(target)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db(db_path: Path | None = None, *, force_reset: bool = False) -> None:
    target = db_path or settings.db_path
    with get_connection(target) as conn:
        conn.executescript(SCHEMA_SQL)
        if force_reset:
            _truncate_tables(conn)
        coin_count = conn.execute("SELECT COUNT(*) AS total FROM coins").fetchone()["total"]
        if coin_count == 0:
            _seed_database(conn)
        conn.commit()


def _truncate_tables(conn: sqlite3.Connection) -> None:
    for table in [
        "coins",
        "factor_details",
        "history_points",
        "source_status",
        "system_logs",
        "status_overview",
        "market_snapshots",
        "market_features",
        "pool_scores",
    ]:
        conn.execute(f"DELETE FROM {table}")


def replace_runtime_dataset(
    payload: dict,
    *,
    snapshots: Iterable[dict] | None = None,
    features: Iterable[dict] | None = None,
    pool_scores: Iterable[dict] | None = None,
    db_path: Path | None = None,
) -> None:
    target = db_path or settings.db_path
    with get_connection(target) as conn:
        _truncate_tables(conn)
        _insert_coins(conn, payload["coins"])
        _insert_factor_rows(conn, payload["factorRows"])
        _insert_history_rows(conn, payload["historyRows"])
        _insert_sources(conn, payload["sources"])
        _insert_logs(conn, payload["logs"])
        _insert_overview(conn, payload["overview"])
        if snapshots is not None:
            _insert_market_snapshots(conn, snapshots)
        if features is not None:
            _insert_market_features(conn, features)
        if pool_scores is not None:
            _insert_pool_scores(conn, pool_scores)
        conn.commit()


def _seed_database(conn: sqlite3.Connection) -> None:
    payload = build_seed_payload()
    _insert_coins(conn, payload["coins"])
    _insert_factor_rows(conn, payload["factorRows"])
    _insert_history_rows(conn, payload["historyRows"])
    _insert_sources(conn, payload["sources"])
    _insert_logs(conn, payload["logs"])
    _insert_overview(conn, payload["overview"])
    _insert_market_features(conn, payload["features"])
    _insert_pool_scores(conn, payload["poolScores"])


def _insert_coins(conn: sqlite3.Connection, coins: Iterable[dict]) -> None:
    conn.executemany(
        """
        INSERT INTO coins (
            symbol, base_asset, name, name_zh, logo_text, price, change_24h,
            volume_24h, market_cap, total_score, rank, rank_change,
            momentum, liquidity, derivatives, community, has_futures,
            open_interest, funding_rate, long_short_ratio, oi_change_24h,
            recent_funding_rates, tags, updated_at
        ) VALUES (
            :symbol, :baseAsset, :name, :nameZh, :logoText, :price, :change24h,
            :volume24h, :marketCap, :totalScore, :rank, :rankChange,
            :momentum, :liquidity, :derivatives, :community, :hasFutures,
            :openInterest, :fundingRate, :longShortRatio, :oiChange24h,
            :recentFundingRates, :tags, :updatedAt
        )
        """,
        [
            {
                **coin,
                "momentum": coin["factors"]["momentum"],
                "liquidity": coin["factors"]["liquidity"],
                "derivatives": coin["factors"]["derivatives"],
                "community": coin["factors"]["community"],
                "hasFutures": 1 if coin["hasFutures"] else 0,
                "recentFundingRates": json.dumps(coin["recentFundingRates"]),
                "tags": json.dumps(coin["tags"]),
            }
            for coin in coins
        ],
    )


def _insert_factor_rows(conn: sqlite3.Connection, rows: Iterable[dict]) -> None:
    conn.executemany(
        """
        INSERT INTO factor_details (
            symbol, category, label, score, subfactor_key, subfactor_name,
            raw_value, z_score, weight, contribution, explanation
        ) VALUES (
            :symbol, :category, :label, :score, :subFactorKey, :subFactorName,
            :rawValue, :zScore, :weight, :contribution, :explanation
        )
        """,
        rows,
    )


def _insert_history_rows(conn: sqlite3.Connection, rows: Iterable[dict]) -> None:
    conn.executemany(
        """
        INSERT INTO history_points (symbol, timestamp, score, rank, price)
        VALUES (:symbol, :timestamp, :score, :rank, :price)
        """,
        rows,
    )


def _insert_sources(conn: sqlite3.Connection, rows: Iterable[dict]) -> None:
    conn.executemany(
        """
        INSERT INTO source_status (source, status, latency_ms, last_success_at, detail)
        VALUES (:source, :status, :latencyMs, :lastSuccessAt, :detail)
        """,
        rows,
    )


def _insert_logs(conn: sqlite3.Connection, rows: Iterable[dict]) -> None:
    conn.executemany(
        """
        INSERT INTO system_logs (timestamp, level, message)
        VALUES (:timestamp, :level, :message)
        """,
        rows,
    )


def _insert_overview(conn: sqlite3.Connection, overview: dict) -> None:
    conn.execute(
        """
        INSERT INTO status_overview (
            id, computed_at, last_score_at, next_score_at,
            refresh_interval_hours, pool_size, coins_with_futures,
            data_quality, uptime
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            1,
            overview["computedAt"],
            overview["lastScoreAt"],
            overview["nextScoreAt"],
            overview["refreshIntervalHours"],
            overview["poolSize"],
            overview["coinsWithFutures"],
            overview["dataQuality"],
            overview["uptime"],
        ),
    )


def _insert_market_snapshots(conn: sqlite3.Connection, rows: Iterable[dict]) -> None:
    conn.execute("DELETE FROM market_snapshots")
    conn.executemany(
        """
        INSERT INTO market_snapshots (
            symbol, snapshot_time, price, price_change_24h, quote_volume_24h,
            market_cap, open_interest, funding_rate, predicted_funding_rate,
            global_long_short_ratio, top_long_short_ratio, top_position_ratio,
            liquidation_notional_24h, source, tags
        ) VALUES (
            :symbol, :snapshotTime, :price, :priceChange24h, :quoteVolume24h,
            :marketCap, :openInterest, :fundingRate, :predictedFundingRate,
            :globalLongShortRatio, :topLongShortRatio, :topPositionRatio,
            :liquidationNotional24h, :source, :tags
        )
        """,
        [{**row, "tags": json.dumps(row["tags"])} for row in rows],
    )


def _insert_market_features(conn: sqlite3.Connection, rows: Iterable[dict]) -> None:
    conn.execute("DELETE FROM market_features")
    conn.executemany(
        """
        INSERT INTO market_features (
            symbol, feature_time, oi_change_1h, oi_change_4h, oi_change_24h,
            turnover_24h, oi_to_volume, oi_to_marketcap, corr_btc_7d, corr_eth_7d,
            funding_rate_mean_24h, funding_rate_std_24h, price_change_1h,
            price_change_24h, distance_to_ma20, price_volatility_7d,
            long_short_ratio_stability, oi_stability_7d, liquidation_to_oi_24h,
            liquidation_to_volume_24h
        ) VALUES (
            :symbol, :featureTime, :oiChange1h, :oiChange4h, :oiChange24h,
            :turnover24h, :oiToVolume, :oiToMarketcap, :corrBtc7d, :corrEth7d,
            :fundingRateMean24h, :fundingRateStd24h, :priceChange1h,
            :priceChange24h, :distanceToMa20, :priceVolatility7d,
            :longShortRatioStability, :oiStability7d, :liquidationToOi24h,
            :liquidationToVolume24h
        )
        """,
        rows,
    )


def _insert_pool_scores(conn: sqlite3.Connection, rows: Iterable[dict]) -> None:
    conn.execute("DELETE FROM pool_scores")
    conn.executemany(
        """
        INSERT INTO pool_scores (
            symbol, score_time, momentum_score, trend_score, mean_reversion_score,
            ls_game_score, momentum_direction, mean_reversion_direction,
            ls_game_direction, primary_pool, primary_score, reason_tags
        ) VALUES (
            :symbol, :scoreTime, :momentumScore, :trendScore, :meanReversionScore,
            :lsGameScore, :momentumDirection, :meanReversionDirection,
            :lsGameDirection, :primaryPool, :primaryScore, :reasonTags
        )
        """,
        [{**row, "reasonTags": json.dumps(row["reasonTags"])} for row in rows],
    )
