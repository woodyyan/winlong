from __future__ import annotations

from math import isfinite


class PoolScoringService:
    POOL_NAMES = ("momentum", "trend", "meanReversion", "lsGame")
    POOL_ENTRY_THRESHOLDS = {
        "momentum": 50.0,
        "trend": 55.0,
        "meanReversion": 50.0,
        "lsGame": 50.0,
    }

    def build_features_and_scores(self, rows: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
        features = [self._build_feature(row) for row in rows]
        self._attach_pool_scores(features)
        row_map = {row["symbol"]: row for row in rows}

        scored_rows: list[dict] = []
        pool_scores: list[dict] = []
        for feature in features:
            row = row_map[feature["symbol"]]
            row["primaryPool"] = feature["primaryPool"]
            row["primaryScore"] = feature["primaryScore"]
            row["poolScores"] = {
                "momentum": feature["momentumScore"],
                "trend": feature["trendScore"],
                "meanReversion": feature["meanReversionScore"],
                "lsGame": feature["lsGameScore"],
            }
            row["poolMemberships"] = feature["poolMemberships"]
            row["reasonTags"] = feature["reasonTags"]
            scored_rows.append(row)
            pool_scores.append(
                {
                    "symbol": feature["symbol"],
                    "scoreTime": feature["featureTime"],
                    "momentumScore": feature["momentumScore"],
                    "trendScore": feature["trendScore"],
                    "meanReversionScore": feature["meanReversionScore"],
                    "lsGameScore": feature["lsGameScore"],
                    "momentumDirection": feature["momentumDirection"],
                    "meanReversionDirection": feature["meanReversionDirection"],
                    "lsGameDirection": feature["lsGameDirection"],
                    "primaryPool": feature["primaryPool"],
                    "primaryScore": feature["primaryScore"],
                    "poolMemberships": feature["poolMemberships"],
                    "reasonTags": feature["reasonTags"],
                }
            )

        return scored_rows, features, pool_scores

    def _build_feature(self, row: dict) -> dict:
        funding_rate = self._num(row.get("fundingRate"))
        funding_mean = self._num(row.get("fundingRateMean24h"), funding_rate)
        predicted_funding = self._num(row.get("predictedFundingRate"), funding_mean)
        oi = self._num(row.get("openInterest"))
        market_cap = max(self._num(row.get("marketCap"), 0), 1.0)
        volume = max(self._num(row.get("volume24h"), 0), 1.0)
        price_change_24h = self._num(row.get("change24h"))
        price_change_1h = self._num(row.get("priceChange1h"), price_change_24h / 24)
        long_short_ratio = max(self._num(row.get("longShortRatio"), 1.0), 0.01)
        long_short_mean = max(self._num(row.get("longShortRatioMean24h"), long_short_ratio), 0.01)
        top_trader_spread = self._num(row.get("topTraderSpread"))
        crowding_score = self._num(row.get("crowdingScore"), abs(long_short_ratio - 1) + top_trader_spread)
        oi_change_24h = self._num(row.get("oiChange24h"))
        liquidation_to_oi = self._num(row.get("liquidationToOi24h"))
        liquidation_to_volume = self._num(row.get("liquidationToVolume24h"))

        return {
            "symbol": row["symbol"],
            "featureTime": row["updatedAt"],
            "oiChange1h": self._num(row.get("oiChange1h"), oi_change_24h / 24),
            "oiChange4h": self._num(row.get("oiChange4h"), oi_change_24h / 6),
            "oiChange24h": oi_change_24h,
            "turnover24h": round(volume / market_cap, 6),
            "oiToVolume": round(oi / volume, 6) if volume else 0.0,
            "oiToMarketcap": round(oi / market_cap, 6) if market_cap else 0.0,
            "corrBtc7d": self._num(row.get("corrBtc7d"), 0.55),
            "corrEth7d": self._num(row.get("corrEth7d"), 0.55),
            "fundingRateMean24h": round(funding_mean, 6),
            "fundingRateStd24h": round(self._num(row.get("fundingRateStd24h")), 6),
            "priceChange1h": round(price_change_1h, 4),
            "priceChange24h": round(price_change_24h, 4),
            "distanceToMa20": round(self._num(row.get("distanceToMa20"), price_change_24h / 3), 4),
            "priceVolatility7d": round(self._num(row.get("priceVolatility7d"), abs(price_change_24h) * 0.6), 4),
            "longShortRatioStability": round(self._num(row.get("longShortRatioStability")), 4),
            "oiStability7d": round(self._num(row.get("oiStability7d")), 4),
            "liquidationToOi24h": round(liquidation_to_oi, 6),
            "liquidationToVolume24h": round(liquidation_to_volume, 6),
            "longShortRatio": round(long_short_ratio, 4),
            "longShortRatioMean24h": round(long_short_mean, 4),
            "predictedFundingRate": round(predicted_funding, 6),
            "topTraderSpread": round(top_trader_spread, 4),
            "crowdingScore": round(crowding_score, 4),
        }

    def _attach_pool_scores(self, features: list[dict]) -> None:
        if not features:
            return

        percentile_maps = {
            "oiChange4h": self._percentile_map([feature["oiChange4h"] for feature in features]),
            "oiChange24h": self._percentile_map([feature["oiChange24h"] for feature in features]),
            "oiDrawdown24h": self._percentile_map([max(-feature["oiChange24h"], 0.0) for feature in features]),
            "turnover24h": self._percentile_map([feature["turnover24h"] for feature in features]),
            "priceChangeAbs24h": self._percentile_map([abs(feature["priceChange24h"]) for feature in features]),
            "liquidationToOi24h": self._percentile_map([feature["liquidationToOi24h"] for feature in features]),
            "liquidationToVolume24h": self._percentile_map([feature["liquidationToVolume24h"] for feature in features]),
            "priceDislocation": self._percentile_map([abs(feature["distanceToMa20"]) for feature in features]),
            "fundingRateAbs24h": self._percentile_map([abs(feature["fundingRateMean24h"]) for feature in features]),
            "predictedFundingAbs": self._percentile_map([abs(feature["predictedFundingRate"]) for feature in features]),
            "fundingRateStd24h": self._percentile_map([feature["fundingRateStd24h"] for feature in features], higher_is_better=False),
            "oiStability7d": self._percentile_map([feature["oiStability7d"] for feature in features], higher_is_better=False),
            "longShortRatioStability": self._percentile_map([feature["longShortRatioStability"] for feature in features], higher_is_better=False),
            "oiToVolume": self._percentile_map([feature["oiToVolume"] for feature in features]),
            "oiToMarketcap": self._percentile_map([feature["oiToMarketcap"] for feature in features]),
            "crowdingScore": self._percentile_map([feature["crowdingScore"] for feature in features]),
            "topTraderSpread": self._percentile_map([feature["topTraderSpread"] for feature in features]),
            "priceAbsorption": self._percentile_map(
                [self._safe_div(feature["crowdingScore"], abs(feature["priceChange1h"]) + 0.75) for feature in features]
            ),
        }

        for feature in features:
            avg_corr = (feature["corrBtc7d"] + feature["corrEth7d"]) / 2
            oi_growth_score = 0.55 * percentile_maps["oiChange24h"][feature["oiChange24h"]] + 0.45 * percentile_maps["oiChange4h"][feature["oiChange4h"]]
            breakout_score = 0.65 * percentile_maps["priceChangeAbs24h"][abs(feature["priceChange24h"])] + 0.35 * self._direction_followthrough_score(feature)
            liquidation_spike_score = 0.55 * percentile_maps["liquidationToOi24h"][feature["liquidationToOi24h"]] + 0.45 * percentile_maps["liquidationToVolume24h"][feature["liquidationToVolume24h"]]
            momentum_score = (
                0.4 * oi_growth_score
                + 0.2 * percentile_maps["turnover24h"][feature["turnover24h"]]
                + 0.2 * breakout_score
                + 0.2 * liquidation_spike_score
            )

            correlation_score = self._corr_band_score(avg_corr)
            oi_trend_score = 0.7 * percentile_maps["oiChange24h"][feature["oiChange24h"]] + 0.3 * percentile_maps["oiStability7d"][feature["oiStability7d"]]
            consensus_score = 0.6 * self._range_score(feature["longShortRatioMean24h"], 0.95, 1.05) + 0.4 * percentile_maps["longShortRatioStability"][feature["longShortRatioStability"]]
            funding_health_score = 0.7 * self._range_score(abs(feature["fundingRateMean24h"]), 0.0, 0.00015) + 0.3 * percentile_maps["fundingRateStd24h"][feature["fundingRateStd24h"]]
            trend_score = (
                0.3 * correlation_score
                + 0.25 * oi_trend_score
                + 0.25 * consensus_score
                + 0.2 * funding_health_score
            )
            if feature["priceChange24h"] < 0:
                trend_score *= 0.88

            dislocation_score = 0.5 * percentile_maps["priceDislocation"][abs(feature["distanceToMa20"])] + 0.5 * percentile_maps["priceChangeAbs24h"][abs(feature["priceChange24h"])]
            funding_extreme_score = percentile_maps["fundingRateAbs24h"][abs(feature["fundingRateMean24h"])]
            oi_unwind_score = percentile_maps["oiDrawdown24h"][max(-feature["oiChange24h"], 0.0)]
            mean_reversion_score = (
                0.4 * liquidation_spike_score
                + 0.3 * dislocation_score
                + 0.2 * funding_extreme_score
                + 0.1 * oi_unwind_score
            )
            if abs(feature["priceChange24h"]) >= 8:
                mean_reversion_score += 5

            divergence_score = (
                0.5 * percentile_maps["crowdingScore"][feature["crowdingScore"]]
                + 0.25 * percentile_maps["priceAbsorption"][self._safe_div(feature["crowdingScore"], abs(feature["priceChange1h"]) + 0.75)]
                + 0.25 * percentile_maps["topTraderSpread"][feature["topTraderSpread"]]
            )
            funding_alignment_score = 0.65 * percentile_maps["predictedFundingAbs"][abs(feature["predictedFundingRate"])] + 0.35 * self._ls_alignment_score(feature)
            ls_game_score = (
                0.4 * divergence_score
                + 0.3 * percentile_maps["oiToVolume"][feature["oiToVolume"]]
                + 0.2 * percentile_maps["oiToMarketcap"][feature["oiToMarketcap"]]
                + 0.1 * funding_alignment_score
            )

            pool_map = {
                "momentum": round(self._clamp(momentum_score), 1),
                "trend": round(self._clamp(trend_score), 1),
                "meanReversion": round(self._clamp(mean_reversion_score), 1),
                "lsGame": round(self._clamp(ls_game_score), 1),
            }
            primary_pool = max(self.POOL_NAMES, key=lambda pool: (pool_map[pool], -self.POOL_NAMES.index(pool)))
            feature["momentumScore"] = pool_map["momentum"]
            feature["trendScore"] = pool_map["trend"]
            feature["meanReversionScore"] = pool_map["meanReversion"]
            feature["lsGameScore"] = pool_map["lsGame"]
            feature["momentumDirection"] = "long" if feature["priceChange24h"] >= 0 else "short"
            feature["meanReversionDirection"] = self._mean_reversion_direction(feature)
            feature["lsGameDirection"] = self._ls_game_direction(feature)
            feature["primaryPool"] = primary_pool
            feature["primaryScore"] = pool_map[primary_pool]
            feature["poolMemberships"] = self.memberships_from_pool_scores(pool_map, primary_pool=primary_pool)
            feature["reasonTags"] = self._build_reason_tags(feature, primary_pool)

    @classmethod
    def memberships_from_pool_scores(
        cls,
        pool_scores: dict[str, float],
        *,
        primary_pool: str | None = None,
    ) -> list[str]:
        memberships = [
            pool
            for pool in cls.POOL_NAMES
            if pool_scores.get(pool, 0.0) >= cls.POOL_ENTRY_THRESHOLDS[pool]
        ]
        if memberships:
            return memberships

        if primary_pool is None and pool_scores:
            primary_pool = max(cls.POOL_NAMES, key=lambda pool: (pool_scores.get(pool, 0.0), -cls.POOL_NAMES.index(pool)))
        return [primary_pool] if primary_pool else []

    def _percentile_map(self, values: list[float], *, higher_is_better: bool = True) -> dict[float, float]:
        if not values:
            return {0.0: 50.0}

        unique_values = sorted(set(values))
        total = max(len(unique_values) - 1, 1)
        score_map: dict[float, float] = {}
        for index, value in enumerate(unique_values):
            base_score = 100 * (index / total) if total else 100.0
            score_map[value] = round(base_score if higher_is_better else 100 - base_score, 1)
        if len(unique_values) == 1:
            only = unique_values[0]
            score_map[only] = 100.0
        return score_map

    def _direction_followthrough_score(self, feature: dict) -> float:
        same_direction = (feature["priceChange24h"] >= 0 and feature["priceChange1h"] >= 0) or (
            feature["priceChange24h"] < 0 and feature["priceChange1h"] < 0
        )
        followthrough = min(abs(feature["priceChange1h"]) * 12, 100)
        return round(55 + followthrough * 0.45, 1) if same_direction else round(max(20.0, 55 - followthrough * 0.5), 1)

    def _corr_band_score(self, value: float) -> float:
        return self._range_score(value, 0.6, 0.8)

    def _range_score(self, value: float, low: float, high: float) -> float:
        if value < low:
            width = max(abs(low), 1e-6)
            return round(max(0.0, 100 - ((low - value) / width) * 100), 1)
        if value > high:
            width = max(abs(high), 1e-6)
            return round(max(0.0, 100 - ((value - high) / width) * 100), 1)
        return 100.0

    def _ls_alignment_score(self, feature: dict) -> float:
        ratio = feature["longShortRatio"]
        funding = feature["predictedFundingRate"]
        if ratio < 0.98 and funding <= 0:
            return 100.0
        if ratio > 1.02 and funding >= 0:
            return 100.0
        return 45.0

    def _mean_reversion_direction(self, feature: dict) -> str:
        if feature["priceChange24h"] <= 0 or feature["fundingRateMean24h"] <= 0:
            return "rebound-long"
        return "reversal-short"

    def _ls_game_direction(self, feature: dict) -> str:
        if feature["longShortRatio"] < 0.98 and feature["predictedFundingRate"] <= 0:
            return "short-squeeze candidate"
        if feature["longShortRatio"] > 1.02 and feature["predictedFundingRate"] >= 0:
            return "long-squeeze candidate"
        return "two-way squeeze candidate"

    def _build_reason_tags(self, feature: dict, primary_pool: str) -> list[str]:
        if primary_pool == "momentum":
            return [
                f"24h/4h OI 变化 {feature['oiChange24h']:.2f}% / {feature['oiChange4h']:.2f}%",
                f"24h 换手率 {feature['turnover24h']:.3f}",
                f"24h 涨跌幅 {feature['priceChange24h']:.2f}%",
            ]
        if primary_pool == "trend":
            return [
                f"7d 相关性 BTC/ETH {feature['corrBtc7d']:.2f} / {feature['corrEth7d']:.2f}",
                f"多空比均值/稳定度 {feature['longShortRatioMean24h']:.2f} / {feature['longShortRatioStability']:.3f}",
                f"24h 平均资金费率 {feature['fundingRateMean24h']:.5f}",
            ]
        if primary_pool == "meanReversion":
            return [
                f"均线偏离 {feature['distanceToMa20']:.2f}%",
                f"强平代理 OI/成交量 {feature['liquidationToOi24h']:.3f} / {feature['liquidationToVolume24h']:.3f}",
                f"24h OI 回落 {feature['oiChange24h']:.2f}%",
            ]
        return [
            f"多空比分歧 {feature['longShortRatio']:.2f}",
            f"OI/成交量 {feature['oiToVolume']:.3f}",
            f"OI/市值 {feature['oiToMarketcap']:.3f}",
        ]

    def _num(self, value: float | int | None, default: float = 0.0) -> float:
        if value is None:
            return float(default)
        numeric = float(value)
        if not isfinite(numeric):
            return float(default)
        return numeric

    def _safe_div(self, numerator: float, denominator: float) -> float:
        if denominator == 0:
            return 0.0
        return numerator / denominator

    def _clamp(self, value: float, low: float = 0.0, high: float = 100.0) -> float:
        return max(low, min(high, value))
