from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone


BASE_TIME = datetime(2026, 4, 22, 8, 0, tzinfo=timezone.utc)
REFRESH_INTERVAL_HOURS = 4


CATEGORY_TEMPLATES = {
    "momentum": {
        "label": "量价动量",
        "subFactors": [
            ("mom_7", "7日动量", "衡量过去一周价格趋势强度"),
            ("rsi_14", "RSI(14)", "衡量近期多空强弱，避免单纯追高"),
            ("boll_pos", "布林带位置", "判断当前价格在波动区间中的相对位置"),
            ("vol_dev", "成交量偏离", "观察量能是否在趋势形成时同步放大"),
            ("var_ret", "波动率调整收益", "比较上涨质量而不只比较涨幅"),
        ],
    },
    "liquidity": {
        "label": "流动性",
        "subFactors": [
            ("log_vol", "对数成交量", "压缩极端量级差异，保留排序关系"),
            ("log_mcap", "对数市值", "避免头部币种直接吞噬全部分布"),
            ("depth_score", "订单簿深度", "衡量 5% 价格区间内可承接挂单规模"),
            ("mcap_rank_inv", "市值排名倒数", "头部排名代表更稳的市场关注度"),
            ("turnover", "换手率", "观察资金活跃度是否处在健康区间"),
        ],
    },
    "derivatives": {
        "label": "衍生品情绪",
        "subFactors": [
            ("oi_abs", "OI绝对值", "观察合约市场是否有足够参与深度"),
            ("oi_change", "OI变化率", "识别杠杆资金是否持续流入"),
            ("funding", "资金费率评分", "费率过高或过低都代表情绪过热"),
            ("lsr_top", "大户多空比", "观察高净值账户的偏向是否极端"),
            ("lsr_global", "全局多空比", "衡量整体账户结构是否失衡"),
        ],
    },
    "community": {
        "label": "社区开发",
        "subFactors": [
            ("gh_stars", "GitHub 星标", "衡量开源项目的开发者关注度"),
            ("community", "社区活跃度", "衡量用户讨论与社交传播情况"),
            ("trending", "趋势热度", "结合搜索热度与榜单活跃度"),
        ],
    },
}


COIN_BLUEPRINTS = [
    {
        "symbol": "BTCUSDT",
        "baseAsset": "BTC",
        "name": "Bitcoin",
        "nameZh": "比特币",
        "logoText": "₿",
        "price": 97500.0,
        "change24h": 2.35,
        "volume24h": 28_500_000_000.0,
        "marketCap": 1_920_000_000_000.0,
        "totalScore": 87.5,
        "rankChange": 0,
        "factors": {"momentum": 85.0, "liquidity": 98.0, "derivatives": 78.0, "community": 90.0},
        "hasFutures": True,
        "openInterest": 12_000_000_000.0,
        "fundingRate": 0.0001,
        "longShortRatio": 1.85,
        "oiChange24h": 0.023,
        "recentFundingRates": [0.0001, 0.00008, 0.00011, 0.00012, 0.00009, 0.0001],
        "tags": ["core", "high-liquidity"],
    },
    {
        "symbol": "ETHUSDT",
        "baseAsset": "ETH",
        "name": "Ethereum",
        "nameZh": "以太坊",
        "logoText": "Ξ",
        "price": 3450.0,
        "change24h": 1.82,
        "volume24h": 14_200_000_000.0,
        "marketCap": 415_000_000_000.0,
        "totalScore": 84.2,
        "rankChange": 1,
        "factors": {"momentum": 82.0, "liquidity": 95.0, "derivatives": 81.0, "community": 88.0},
        "hasFutures": True,
        "openInterest": 8_100_000_000.0,
        "fundingRate": 0.00008,
        "longShortRatio": 1.62,
        "oiChange24h": 0.018,
        "recentFundingRates": [0.00008, 0.00009, 0.00007, 0.00006, 0.00008, 0.00008],
        "tags": ["smart-contract", "high-liquidity"],
    },
    {
        "symbol": "SOLUSDT",
        "baseAsset": "SOL",
        "name": "Solana",
        "nameZh": "索拉纳",
        "logoText": "◎",
        "price": 142.3,
        "change24h": 5.67,
        "volume24h": 3_200_000_000.0,
        "marketCap": 65_000_000_000.0,
        "totalScore": 82.1,
        "rankChange": 2,
        "factors": {"momentum": 91.0, "liquidity": 85.0, "derivatives": 88.0, "community": 72.0},
        "hasFutures": True,
        "openInterest": 3_400_000_000.0,
        "fundingRate": 0.0005,
        "longShortRatio": 1.62,
        "oiChange24h": 0.056,
        "recentFundingRates": [0.00042, 0.00048, 0.00051, 0.0005, 0.00045, 0.00047],
        "tags": ["top-mover", "smart-beta"],
    },
    {
        "symbol": "BNBUSDT",
        "baseAsset": "BNB",
        "name": "BNB",
        "nameZh": "币安币",
        "logoText": "◇",
        "price": 612.5,
        "change24h": -0.34,
        "volume24h": 1_950_000_000.0,
        "marketCap": 89_000_000_000.0,
        "totalScore": 79.8,
        "rankChange": -1,
        "factors": {"momentum": 68.0, "liquidity": 92.0, "derivatives": 75.0, "community": 79.0},
        "hasFutures": True,
        "openInterest": 2_750_000_000.0,
        "fundingRate": 0.00004,
        "longShortRatio": 1.24,
        "oiChange24h": 0.012,
        "recentFundingRates": [0.00002, 0.00004, 0.00003, 0.00004, 0.00005, 0.00004],
        "tags": ["exchange", "yield"],
    },
    {
        "symbol": "XRPUSDT",
        "baseAsset": "XRP",
        "name": "XRP",
        "nameZh": "瑞波币",
        "logoText": "✕",
        "price": 0.68,
        "change24h": 3.18,
        "volume24h": 2_400_000_000.0,
        "marketCap": 39_000_000_000.0,
        "totalScore": 76.3,
        "rankChange": 3,
        "factors": {"momentum": 77.0, "liquidity": 82.0, "derivatives": 69.0, "community": 74.0},
        "hasFutures": True,
        "openInterest": 1_150_000_000.0,
        "fundingRate": -0.00002,
        "longShortRatio": 1.14,
        "oiChange24h": 0.034,
        "recentFundingRates": [-0.00001, -0.00002, 0.0, 0.00001, -0.00001, -0.00002],
        "tags": ["payments", "rebound"],
    },
    {
        "symbol": "TAOUSDT",
        "baseAsset": "TAO",
        "name": "Bittensor",
        "nameZh": "比特张量",
        "logoText": "τ",
        "price": 488.4,
        "change24h": 7.42,
        "volume24h": 620_000_000.0,
        "marketCap": 4_100_000_000.0,
        "totalScore": 75.6,
        "rankChange": 4,
        "factors": {"momentum": 94.0, "liquidity": 61.0, "derivatives": 58.0, "community": 80.0},
        "hasFutures": False,
        "openInterest": None,
        "fundingRate": None,
        "longShortRatio": None,
        "oiChange24h": None,
        "recentFundingRates": [],
        "tags": ["ai", "emerging"],
    },
    {
        "symbol": "LINKUSDT",
        "baseAsset": "LINK",
        "name": "Chainlink",
        "nameZh": "预言机",
        "logoText": "⬡",
        "price": 18.6,
        "change24h": 1.04,
        "volume24h": 950_000_000.0,
        "marketCap": 11_000_000_000.0,
        "totalScore": 73.2,
        "rankChange": 0,
        "factors": {"momentum": 70.0, "liquidity": 72.0, "derivatives": 71.0, "community": 79.0},
        "hasFutures": True,
        "openInterest": 540_000_000.0,
        "fundingRate": 0.00003,
        "longShortRatio": 1.08,
        "oiChange24h": 0.015,
        "recentFundingRates": [0.00003, 0.00003, 0.00002, 0.00003, 0.00004, 0.00003],
        "tags": ["oracle", "defensive"],
    },
    {
        "symbol": "DOGEUSDT",
        "baseAsset": "DOGE",
        "name": "Dogecoin",
        "nameZh": "狗狗币",
        "logoText": "Ð",
        "price": 0.22,
        "change24h": -1.26,
        "volume24h": 1_550_000_000.0,
        "marketCap": 31_000_000_000.0,
        "totalScore": 69.9,
        "rankChange": -2,
        "factors": {"momentum": 58.0, "liquidity": 80.0, "derivatives": 66.0, "community": 72.0},
        "hasFutures": True,
        "openInterest": 880_000_000.0,
        "fundingRate": 0.00009,
        "longShortRatio": 1.92,
        "oiChange24h": -0.011,
        "recentFundingRates": [0.00012, 0.00011, 0.00009, 0.00008, 0.00009, 0.00009],
        "tags": ["meme", "volatile"],
    },
]


def iso_timestamp(days_ago: int = 0, hours_offset: int = 0) -> str:
    dt = BASE_TIME - timedelta(days=days_ago) + timedelta(hours=hours_offset)
    return dt.isoformat().replace("+00:00", "Z")


def build_factor_rows(coin: dict) -> list[dict]:
    rows: list[dict] = []
    for category_key, category_info in CATEGORY_TEMPLATES.items():
        category_score = coin["factors"][category_key]
        for index, (sub_key, sub_name, explanation) in enumerate(category_info["subFactors"], start=1):
            weight = round(1 / len(category_info["subFactors"]), 2)
            modifier = (index - (len(category_info["subFactors"]) + 1) / 2) * 1.4
            raw_value = round(max(category_score + modifier, 1), 2)
            z_score = round(((raw_value - 50) / 18), 2)
            contribution = round(category_score * weight, 2)
            rows.append(
                {
                    "symbol": coin["symbol"],
                    "category": category_key,
                    "label": category_info["label"],
                    "score": category_score,
                    "subFactorKey": sub_key,
                    "subFactorName": sub_name,
                    "rawValue": raw_value,
                    "zScore": z_score,
                    "weight": weight,
                    "contribution": contribution,
                    "explanation": explanation,
                }
            )
    return rows


def build_history_rows(coin: dict, rank: int) -> list[dict]:
    rows: list[dict] = []
    for day in range(29, -1, -1):
        angle = (29 - day) / 4
        score = round(coin["totalScore"] - math.sin(angle) * 2.4 + math.cos(angle / 2) * 0.8, 1)
        price = round(coin["price"] * (1 - day * 0.004 + math.sin(angle) * 0.03), 4 if coin["price"] < 5 else 2)
        historical_rank = max(1, min(len(COIN_BLUEPRINTS), rank + int(math.sin(angle) * 1.8) - coin["rankChange"]))
        rows.append(
            {
                "symbol": coin["symbol"],
                "timestamp": iso_timestamp(days_ago=day),
                "score": score,
                "rank": historical_rank,
                "price": price,
            }
        )
    return rows


def build_seed_payload() -> dict:
    coins: list[dict] = []
    factor_rows: list[dict] = []
    history_rows: list[dict] = []

    for rank, blueprint in enumerate(COIN_BLUEPRINTS, start=1):
        coin = {
            **blueprint,
            "rank": rank,
            "updatedAt": iso_timestamp(),
        }
        coins.append(coin)
        factor_rows.extend(build_factor_rows(coin))
        history_rows.extend(build_history_rows(coin, rank))

    sources = [
        {
            "source": "Binance Spot",
            "status": "ok",
            "latencyMs": 1230,
            "lastSuccessAt": iso_timestamp(hours_offset=-1),
            "detail": "行情、K线、成交量均已刷新",
        },
        {
            "source": "Binance Futures",
            "status": "ok",
            "latencyMs": 2140,
            "lastSuccessAt": iso_timestamp(hours_offset=-1),
            "detail": "OI、资金费率、多空比均可用",
        },
        {
            "source": "CoinGecko",
            "status": "stale",
            "latencyMs": 3456,
            "lastSuccessAt": iso_timestamp(hours_offset=-2),
            "detail": "社区数据存在轻微陈旧，当前使用缓存兜底",
        },
    ]

    logs = [
        {"timestamp": iso_timestamp(hours_offset=-4), "level": "info", "message": "评分完成：8 个币种已更新"},
        {"timestamp": iso_timestamp(hours_offset=-4), "level": "info", "message": "现货采集完成：Binance Spot 响应正常"},
        {"timestamp": iso_timestamp(hours_offset=-3), "level": "warn", "message": "CoinGecko 命中速率限制，已回退缓存"},
        {"timestamp": iso_timestamp(hours_offset=-1), "level": "info", "message": "合约情绪数据已刷新"},
    ]

    overview = {
        "computedAt": iso_timestamp(),
        "lastScoreAt": iso_timestamp(),
        "nextScoreAt": iso_timestamp(hours_offset=REFRESH_INTERVAL_HOURS),
        "refreshIntervalHours": REFRESH_INTERVAL_HOURS,
        "poolSize": len(coins),
        "coinsWithFutures": sum(1 for coin in coins if coin["hasFutures"]),
        "dataQuality": "degraded",
        "uptime": "3天 7小时",
    }

    return {
        "coins": coins,
        "factorRows": factor_rows,
        "historyRows": history_rows,
        "sources": sources,
        "logs": logs,
        "overview": overview,
    }
