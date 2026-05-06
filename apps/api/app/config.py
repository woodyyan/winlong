from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


_CONFIG_PATH = Path(__file__).resolve()
_PARENTS = _CONFIG_PATH.parents
ROOT_DIR = Path(
    os.getenv(
        "WINLONG_ROOT_DIR",
        _PARENTS[3] if len(_PARENTS) > 3 else _PARENTS[len(_PARENTS) - 1],
    )
)
DEFAULT_DB_PATH = ROOT_DIR / "data" / "winlong.db"


@dataclass(frozen=True)
class Settings:
    app_name: str = "Winlong API"
    app_version: str = "0.1.0"
    db_path: Path = Path(os.getenv("WINLONG_DB_PATH", DEFAULT_DB_PATH))
    enable_sync_on_start: bool = os.getenv("WINLONG_ENABLE_SYNC_ON_START", "false").lower() == "true"
    refresh_interval_minutes: int = int(os.getenv("WINLONG_REFRESH_INTERVAL_MINUTES", "15"))
    binance_spot_base_url: str = os.getenv("BINANCE_SPOT_BASE_URL", "https://api.binance.com")
    binance_futures_base_url: str = os.getenv("BINANCE_FUTURES_BASE_URL", "https://fapi.binance.com")
    coingecko_base_url: str = os.getenv("COINGECKO_BASE_URL", "https://api.coingecko.com/api/v3")
    sync_timeout_seconds: float = float(os.getenv("WINLONG_SYNC_TIMEOUT_SECONDS", "20"))
    min_market_cap_usd: float = float(os.getenv("WINLONG_MIN_MARKET_CAP_USD", "10000000"))
    universe_limit: int = int(os.getenv("WINLONG_UNIVERSE_LIMIT", "150"))
    allowed_origins_raw: str = os.getenv(
        "WINLONG_ALLOWED_ORIGINS",
        "http://localhost:3001,http://127.0.0.1:3001",
    )

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins_raw.split(",") if origin.strip()]


settings = Settings()
