from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from app.config import settings
from app.db import get_connection


class CoinNotFoundError(Exception):
    pass


class WinlongService:
    ALLOWED_SORT_FIELDS = {
        "rank": "rank",
        "score": "total_score",
        "price": "price",
        "change24h": "change_24h",
        "momentum": "momentum",
        "liquidity": "liquidity",
        "derivatives": "derivatives",
        "community": "community",
        "marketCap": "market_cap",
        "volume24h": "volume_24h",
    }

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or settings.db_path

    def list_coins(
        self,
        *,
        limit: int,
        offset: int,
        min_score: float,
        sort_by: str,
        order: str,
        q: str | None = None,
        tag: str | None = None,
    ) -> dict:
        sort_column = self.ALLOWED_SORT_FIELDS.get(sort_by, "rank")
        order_value = "DESC" if order.lower() == "desc" else "ASC"
        where_clauses = ["total_score >= ?"]
        params: list[object] = [min_score]

        if q:
            where_clauses.append("(symbol LIKE ? OR name LIKE ? OR name_zh LIKE ?)")
            like = f"%{q.upper()}%"
            params.extend([like, f"%{q}%", f"%{q}%"])

        if tag:
            where_clauses.append("tags LIKE ?")
            params.append(f"%{tag}%")

        where_sql = " AND ".join(where_clauses)

        with get_connection(self.db_path) as conn:
            total = conn.execute(
                f"SELECT COUNT(*) AS total FROM coins WHERE {where_sql}",
                params,
            ).fetchone()["total"]

            rows = conn.execute(
                f"""
                SELECT * FROM coins
                WHERE {where_sql}
                ORDER BY {sort_column} {order_value}, rank ASC
                LIMIT ? OFFSET ?
                """,
                [*params, limit, offset],
            ).fetchall()

            overview = conn.execute("SELECT * FROM status_overview WHERE id = 1").fetchone()

        return {
            "code": 0,
            "message": "ok",
            "data": {
                "computedAt": overview["computed_at"],
                "totalCoins": total,
                "returnedCount": len(rows),
                "dataQuality": overview["data_quality"],
                "coins": [self._serialize_coin(row) for row in rows],
            },
        }

    def get_coin_detail(self, symbol: str) -> dict:
        normalized = symbol.upper()
        with get_connection(self.db_path) as conn:
            row = conn.execute("SELECT * FROM coins WHERE symbol = ?", (normalized,)).fetchone()
            if row is None:
                raise CoinNotFoundError(normalized)

            factor_rows = conn.execute(
                """
                SELECT * FROM factor_details
                WHERE symbol = ?
                ORDER BY category ASC, id ASC
                """,
                (normalized,),
            ).fetchall()

        grouped: dict[str, dict] = {}
        for factor in factor_rows:
            category_key = factor["category"]
            if category_key not in grouped:
                grouped[category_key] = {
                    "category": category_key,
                    "label": factor["label"],
                    "score": factor["score"],
                    "subFactors": [],
                }
            grouped[category_key]["subFactors"].append(
                {
                    "key": factor["subfactor_key"],
                    "name": factor["subfactor_name"],
                    "rawValue": factor["raw_value"],
                    "zScore": factor["z_score"],
                    "weight": factor["weight"],
                    "contribution": factor["contribution"],
                    "explanation": factor["explanation"],
                }
            )

        return {
            "code": 0,
            "message": "ok",
            "data": {
                "coin": self._serialize_coin(row),
                "factorDetails": list(grouped.values()),
                "derivatives": {
                    "hasFutures": bool(row["has_futures"]),
                    "openInterest": row["open_interest"],
                    "fundingRate": row["funding_rate"],
                    "longShortRatio": row["long_short_ratio"],
                    "oiChange24h": row["oi_change_24h"],
                    "recentFundingRates": json.loads(row["recent_funding_rates"]),
                },
            },
        }

    def get_coin_history(self, symbol: str, *, days: int) -> dict:
        normalized = symbol.upper()
        with get_connection(self.db_path) as conn:
            coin_row = conn.execute("SELECT 1 FROM coins WHERE symbol = ?", (normalized,)).fetchone()
            if coin_row is None:
                raise CoinNotFoundError(normalized)
            rows = conn.execute(
                """
                SELECT timestamp, score, rank, price
                FROM history_points
                WHERE symbol = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (normalized, days),
            ).fetchall()

        history = [
            {
                "timestamp": row["timestamp"],
                "score": row["score"],
                "rank": row["rank"],
                "price": row["price"],
            }
            for row in reversed(rows)
        ]
        return {"code": 0, "message": "ok", "data": history}

    def get_status(self) -> dict:
        with get_connection(self.db_path) as conn:
            overview = conn.execute("SELECT * FROM status_overview WHERE id = 1").fetchone()
            sources = conn.execute("SELECT * FROM source_status ORDER BY source ASC").fetchall()
            logs = conn.execute("SELECT * FROM system_logs ORDER BY timestamp DESC LIMIT 10").fetchall()

        database_size_mb = round(self._database_size_mb(), 2)
        return {
            "code": 0,
            "message": "ok",
            "data": {
                "overview": {
                    "computedAt": overview["computed_at"],
                    "lastScoreAt": overview["last_score_at"],
                    "nextScoreAt": overview["next_score_at"],
                    "refreshIntervalHours": overview["refresh_interval_hours"],
                    "poolSize": overview["pool_size"],
                    "coinsWithFutures": overview["coins_with_futures"],
                    "dataQuality": overview["data_quality"],
                    "databaseSizeMb": database_size_mb,
                    "uptime": overview["uptime"],
                },
                "sources": [
                    {
                        "source": row["source"],
                        "status": row["status"],
                        "latencyMs": row["latency_ms"],
                        "lastSuccessAt": row["last_success_at"],
                        "detail": row["detail"],
                    }
                    for row in sources
                ],
                "logs": [
                    {
                        "timestamp": row["timestamp"],
                        "level": row["level"],
                        "message": row["message"],
                    }
                    for row in logs
                ],
            },
        }

    def _serialize_coin(self, row: sqlite3.Row) -> dict:
        return {
            "symbol": row["symbol"],
            "baseAsset": row["base_asset"],
            "name": row["name"],
            "nameZh": row["name_zh"],
            "logoText": row["logo_text"],
            "price": row["price"],
            "change24h": row["change_24h"],
            "volume24h": row["volume_24h"],
            "marketCap": row["market_cap"],
            "totalScore": row["total_score"],
            "rank": row["rank"],
            "rankChange": row["rank_change"],
            "factors": {
                "momentum": row["momentum"],
                "liquidity": row["liquidity"],
                "derivatives": row["derivatives"],
                "community": row["community"],
            },
            "hasFutures": bool(row["has_futures"]),
            "openInterest": row["open_interest"],
            "fundingRate": row["funding_rate"],
            "longShortRatio": row["long_short_ratio"],
            "tags": json.loads(row["tags"]),
            "updatedAt": row["updated_at"],
        }

    def _database_size_mb(self) -> float:
        if not self.db_path.exists():
            return 0.0
        return self.db_path.stat().st_size / (1024 * 1024)
