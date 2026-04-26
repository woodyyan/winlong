from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_DB_PATH = ROOT_DIR / "data" / "winlong.db"


@dataclass(frozen=True)
class Settings:
    app_name: str = "Winlong API"
    app_version: str = "0.1.0"
    db_path: Path = Path(os.getenv("WINLONG_DB_PATH", DEFAULT_DB_PATH))
    allowed_origins_raw: str = os.getenv(
        "WINLONG_ALLOWED_ORIGINS",
        "http://localhost:3001,http://127.0.0.1:3001",
    )

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins_raw.split(",") if origin.strip()]


settings = Settings()
