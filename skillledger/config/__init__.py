"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    """Configuration container for the SkillLedger application."""

    debug: bool = field(default_factory=lambda: os.getenv("FLASK_DEBUG", "0") == "1")
    host: str = field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "5000")))
    secret_key: str = field(
        default_factory=lambda: os.getenv(
            "SECRET_KEY", "dev-secret-change-in-production"
        )
    )

    # Database
    database_url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            f"sqlite:///{Path(__file__).resolve().parent.parent.parent / 'data' / 'skillledger.db'}",
        )
    )

    @property
    def database_path(self) -> str:
        """Extract the file path from a sqlite:/// URL."""
        raw = self.database_url
        if raw.startswith("sqlite:///"):
            return raw[len("sqlite:///"):]
        return raw  # pragma: no cover — only sqlite for now

    @classmethod
    def from_env(cls) -> Config:
        """Build a Config instance from the current environment."""
        return cls()
