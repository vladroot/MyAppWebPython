"""Application configuration, mirroring the C# DatabaseOptions / FeatureOptions."""

import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def _getenv(key: str, default: Optional[str] = None) -> Optional[str]:
    """Read an environment variable, falling back to .env values already loaded."""
    value = os.getenv(key)
    if not value or not value.strip():
        return default
    return value


class DatabaseOptions:
    """Connection settings for the three datastores the app talks to."""

    POSTGRES_CONNECTION_KEY = "POSTGRES_CONNECTION"
    MONGO_CONNECTION_KEY = "MONGO_CONNECTION"
    MONGO_DB_KEY = "MONGO_DB"
    SQLITE_CONNECTION_KEY = "SQLITE_CONNECTION"
    REDIS_CONNECTION_KEY = "REDIS_CONNECTION"

    # compose.yaml ships this key misspelled with three n's; we accept both spellings.
    LEGACY_SQLITE_CONNECTION_KEY = "SQLITE_CONNNECTION"

    RUN_MIGRATIONS_KEY = "RUN_MIGRATIONS"
    NOT_CONFIGURED_SUFFIX = " in compose.yaml not set"

    def __init__(self) -> None:
        self.postgres_connection: str = self._required(
            _getenv(self.POSTGRES_CONNECTION_KEY), self.POSTGRES_CONNECTION_KEY
        )
        self.mongo_connection: str = self._required(
            _getenv(self.MONGO_CONNECTION_KEY), self.MONGO_CONNECTION_KEY
        )
        self.mongo_db: str = self._required(
            _getenv(self.MONGO_DB_KEY), self.MONGO_DB_KEY
        )
        self.sqlite_connection: str = self._required(
            _getenv(self.SQLITE_CONNECTION_KEY)
            or _getenv(self.LEGACY_SQLITE_CONNECTION_KEY),
            self.LEGACY_SQLITE_CONNECTION_KEY,
        )
        # Optional: unlike the datastores above, a missing Redis only disables caching.
        self.redis_connection: str = _getenv(self.REDIS_CONNECTION_KEY, "") or ""

    @staticmethod
    def _required(value: Optional[str], key: str) -> str:
        if not value or not value.strip():
            raise RuntimeError(f"{key} not set!")
        return value

    @property
    def is_redis_configured(self) -> bool:
        """True when caching is backed by Redis instead of the in-memory fallback."""
        return bool(self.redis_connection.strip())

    @property
    def missing_keys(self) -> list[str]:
        """The names of every connection setting that is not configured."""
        missing: list[str] = []
        if not self.postgres_connection.strip():
            missing.append(self.POSTGRES_CONNECTION_KEY)
        if not self.mongo_connection.strip():
            missing.append(self.MONGO_CONNECTION_KEY)
        if not self.mongo_db.strip():
            missing.append(self.MONGO_DB_KEY)
        if not self.sqlite_connection.strip():
            missing.append(self.LEGACY_SQLITE_CONNECTION_KEY)
        return missing

    def validate(self) -> Optional[str]:
        """Returns a message naming every unconfigured setting, or None when complete."""
        missing = self.missing_keys
        if not missing:
            return None
        return "; ".join(f"{k}{self.NOT_CONFIGURED_SUFFIX}" for k in missing)


class FeatureOptions:
    """Feature flags / default-value models loaded from configuration."""

    def __init__(self, default_value_models: "DefaultValueModels") -> None:
        self.default_value_models = default_value_models


class DefaultValueModels:
    """Default values for the save/load model and boolean data list."""

    def __init__(
        self,
        save_load_model: "SaveLoadModel",
        bool_datas: list["BoolData"],
    ) -> None:
        self.save_load_model = save_load_model
        self.bool_datas = bool_datas


class SaveLoadModel:
    """Default save/load model."""

    def __init__(
        self,
        name: str = "John Doe",
        age: int = 30,
        weight: float = 84.0,
        money: float = 10.0,
        items: list[str] | None = None,
    ) -> None:
        self.name = name
        self.age = age
        self.weight = weight
        self.money = money
        self.items = items or ["Sword", "Gun", "Pickaxe", "Bubble"]


class BoolData:
    """A single boolean data entry."""

    def __init__(self, value: bool = False) -> None:
        self.value = value