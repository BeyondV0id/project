"""Runtime configuration from environment."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env(key, default=None):
    v = os.getenv(key)
    return v if v not in (None, "") else default


@dataclass
class Settings:
    mock_mode: bool = True
    app_env: str = "dev"
    vlm_provider: str = "mock"
    kb_version: str = "2026.11.1"
    sqlite_path: Path = Path("data/app.db")
    chroma_dir: Path = Path("data/chroma")
    artifacts_dir: Path = Path("data/artifacts")
    max_upload_mb: int = 10
    max_image_side: int = 1024
    max_clarify_rounds: int = 2
    rate_limit_hourly: int = 60

    @classmethod
    def from_env(cls):
        return cls(
            mock_mode=_env("MOCK_MODE", "1") == "1",
            app_env=_env("APP_ENV", "dev") or "dev",
            vlm_provider=_env("VLM_PROVIDER", "mock") or "mock",
            kb_version=_env("KB_VERSION", "2026.11.1") or "2026.11.1",
            sqlite_path=Path(_env("SQLITE_PATH", "data/app.db") or "data/app.db"),
            chroma_dir=Path(_env("CHROMA_DIR", "data/chroma") or "data/chroma"),
            artifacts_dir=Path(_env("ARTIFACTS_DIR", "data/artifacts") or "data/artifacts"),
            max_upload_mb=int(_env("MAX_UPLOAD_MB", "10") or "10"),
            max_image_side=int(_env("MAX_IMAGE_SIDE", "1024") or "1024"),
            max_clarify_rounds=int(_env("MAX_CLARIFY_ROUNDS", "2") or "2"),
            rate_limit_hourly=int(_env("RATE_LIMIT_HOURLY", "60") or "60"),
        )


settings = Settings.from_env()
