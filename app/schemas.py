"""Pydantic schemas for API request/response bodies."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock: int

    model_config = ConfigDict(from_attributes=True)


class DatabaseVersionResponse(BaseModel):
    database: str
    version: Optional[str] = None
    timestamp: datetime


class MongoProbeResponse(BaseModel):
    database: str
    version: Optional[str] = None
    timestamp: datetime
    status: str
    message: Optional[str] = None

    @classmethod
    def ok(cls, version: Optional[str]) -> "MongoProbeResponse":
        return cls(
            database="mongodb",
            version=version,
            timestamp=datetime.utcnow(),
            status="ok",
            message=None,
        )

    @classmethod
    def error(cls, message: str) -> "MongoProbeResponse":
        return cls(
            database="mongodb",
            version=None,
            timestamp=datetime.utcnow(),
            status="error",
            message=message,
        )


class HealthResponse(BaseModel):
    status: str
    message: Optional[str] = None
    error: Optional[str] = None
    missing_keys: Optional[list[str]] = None
    timestamp: datetime

    @classmethod
    def healthy(cls) -> "HealthResponse":
        return cls(
            status="healthy",
            message="Ok",
            timestamp=datetime.utcnow(),
        )

    @classmethod
    def unhealthy(
        cls, error: str, missing_keys: list[str]
    ) -> "HealthResponse":
        return cls(
            status="unhealthy",
            error=error,
            missing_keys=missing_keys,
            timestamp=datetime.utcnow(),
        )


class ApiResponse(BaseModel):
    status: str
    message: str
    timestamp: datetime


class ApiErrorResponse(BaseModel):
    status: str
    error: Optional[str] = None
    timestamp: datetime