from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from app.config import settings
from app.db import get_connection


class CoinNotFoundError(Exception):
    pass


class WinlongService:
    POOL_CONFIG = {
        "momentum": {
            "name": "冲浪池",
            "shortName": "Momentum",
            "description": "抓 OI 与波动同步放大的高活跃币。",
            "directionField": "momentum_direction",
        },
        "trend": {
            "name": "趋势池",
            "shortName": "Trend",
            "description": "筛选相关性稳定、资金结构健康的趋势币。",
            "directionField": None,
        },
        "meanReversion": {
            "name": "逆势池",
            "shortName": "Reversion",
            "description": "寻找情绪极值和 OI 释放后的反弹机会。",
            "directionField": "mean_reversion_direction",
        },
        "lsGame": {
            "name": "博弈池",
            "shortName": "Squeeze",
            "description": "寻找多空拥挤和潜在挤兑方向。",
            "directionField": "ls_game_direction",
        },
    }

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
            pool_score_rows = conn.execute(
                """
                SELECT symbol, momentum_score, trend_score, mean_reversion_score,
                       ls_game_score, primary_pool, primary_score, reason_tags,
                       momentum_direction, mean_reversion_direction, ls_game_direction
                FROM pool_scores
                """
            ).fetchall()
            pool_score_map = {row["symbol"]: row for row in pool_score_rows}

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
                "pools": self._build_pool_summaries(pool_score_rows),
                "coins": [self._serialize_coin(row, pool_score_map.get(row["symbol"])) for row in rows],
            },
        }

    def get_coin_detail(self, symbol: str) -> dict:
        normalized = symbol.upper()
        with get_connection(self.db_path) as conn:
            pool_score_row = conn.execute(
                """
                SELECT symbol, momentum_score, trend_score, mean_reversion_score,
                       ls_game_score, primary_pool, primary_score, reason_tags,
                       momentum_direction, mean_reversion_direction, ls_game_direction
                FROM pool_scores
                WHERE symbol = ?
                ORDER BY score_time DESC
                LIMIT 1
                """,
                (normalized,),
            ).fetchone()
            feature_row = conn.execute(
                """
                SELECT * FROM market_features
                WHERE symbol = ?
                ORDER BY feature_time DESC
                LIMIT 1
                """,
                (normalized,),
            ).fetchone()
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
                "coin": self._serialize_coin(row, pool_score_row),
                "factorDetails": list(grouped.values()),
                "derivatives": {
                    "hasFutures": bool(row["has_futures"]),
                    "openInterest": row["open_interest"],
                    "fundingRate": row["funding_rate"],
                    "longShortRatio": row["long_short_ratio"],
                    "oiChange24h": row["oi_change_24h"],
                    "recentFundingRates": json.loads(row["recent_funding_rates"]),
                },
                "marketFeatures": self._serialize_market_features(feature_row),
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
            runtime_snapshot = conn.execute("SELECT COUNT(*) AS total FROM market_snapshots").fetchone()

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
                    "runtimeData": runtime_snapshot["total"] > 0,
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

    def _serialize_coin(self, row: sqlite3.Row, pool_score_row: sqlite3.Row | None = None) -> dict:
        pool_scores = {
            "momentum": pool_score_row["momentum_score"],
            "trend": pool_score_row["trend_score"],
            "meanReversion": pool_score_row["mean_reversion_score"],
            "lsGame": pool_score_row["ls_game_score"],
        } if pool_score_row else {}
        reason_tags = json.loads(pool_score_row["reason_tags"]) if pool_score_row else []

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
            "primaryPool": pool_score_row["primary_pool"] if pool_score_row else None,
            "primaryScore": pool_score_row["primary_score"] if pool_score_row else None,
            "poolScores": pool_scores,
            "reasonTags": reason_tags,
            "momentumDirection": pool_score_row["momentum_direction"] if pool_score_row else None,
            "meanReversionDirection": pool_score_row["mean_reversion_direction"] if pool_score_row else None,
            "lsGameDirection": pool_score_row["ls_game_direction"] if pool_score_row else None,
            "tags": json.loads(row["tags"]),
            "updatedAt": row["updated_at"],
        }

    def _build_pool_summaries(self, rows: list[sqlite3.Row]) -> list[dict]:
        summaries: list[dict] = []
        for pool_key, config in self.POOL_CONFIG.items():
            score_column = self._pool_score_column(pool_key)
            direction_field = config["directionField"]
            ranked_rows = sorted(rows, key=lambda row: row[score_column], reverse=True)
            if ranked_rows:
                avg_score = round(sum(row[score_column] for row in ranked_rows) / len(ranked_rows), 1)
                leader = ranked_rows[0]
                leader_symbol = leader["symbol"]
                leader_score = leader[score_column]
                leader_direction = leader[direction_field] if direction_field else None
            else:
                avg_score = 0.0
                leader_symbol = None
                leader_score = None
                leader_direction = None

            summaries.append(
                {
                    "key": pool_key,
                    "name": config["name"],
                    "shortName": config["shortName"],
                    "description": config["description"],
                    "count": len(ranked_rows),
                    "avgScore": avg_score,
                    "leaderSymbol": leader_symbol,
                    "leaderScore": leader_score,
                    "leaderDirection": leader_direction,
                }
            )

        return summaries

    def _pool_score_column(self, pool_key: str) -> str:
        return {
            "momentum": "momentum_score",
            "trend": "trend_score",
            "meanReversion": "mean_reversion_score",
            "lsGame": "ls_game_score",
        }[pool_key]

    def _serialize_market_features(self, row: sqlite3.Row | None) -> dict | None:
        if row is None:
            return None

        return {
            "oiChange1h": row["oi_change_1h"],
            "oiChange4h": row["oi_change_4h"],
            "oiChange24h": row["oi_change_24h"],
            "turnover24h": row["turnover_24h"],
            "oiToVolume": row["oi_to_volume"],
            "oiToMarketcap": row["oi_to_marketcap"],
            "corrBtc7d": row["corr_btc_7d"],
            "corrEth7d": row["corr_eth_7d"],
            "fundingRateMean24h": row["funding_rate_mean_24h"],
            "fundingRateStd24h": row["funding_rate_std_24h"],
            "priceChange1h": row["price_change_1h"],
            "priceChange24h": row["price_change_24h"],
            "distanceToMa20": row["distance_to_ma20"],
            "priceVolatility7d": row["price_volatility_7d"],
            "longShortRatioStability": row["long_short_ratio_stability"],
            "oiStability7d": row["oi_stability_7d"],
            "liquidationToOi24h": row["liquidation_to_oi_24h"],
            "liquidationToVolume24h": row["liquidation_to_volume_24h"],
        }

    def _database_size_mb(self) -> float:
        if not self.db_path.exists():
            return 0.0
        return self.db_path.stat().st_size / (1024 * 1024)
