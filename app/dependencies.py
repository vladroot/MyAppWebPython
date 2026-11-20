"""FastAPI dependency providers.

Shared services live on ``app.state`` (populated during the application
lifespan in :mod:`app.main`). These providers return them so route handlers
can declare dependencies with ``Depends(...)`` instead of treating the
service objects as request-body models.

``bind_app`` must be called with the FastAPI instance before the first
request is served.
"""

from app.config import DatabaseOptions, FeatureOptions
from app.repositories.user_repository import UserRepository
from app.services.message_log import ServerMessageLog
from app.services.save_load import SaveLoadController

_app = None


def bind_app(app) -> None:
    """Bind the FastAPI instance so providers can read ``app.state``."""
    global _app
    _app = app


def get_options() -> DatabaseOptions:
    return _app.state.options


def get_feature_options() -> FeatureOptions:
    return _app.state.feature_options


def get_message_log() -> ServerMessageLog:
    return _app.state.message_log


def get_save_load() -> SaveLoadController:
    return _app.state.save_load


def get_user_repository() -> UserRepository:
    return _app.state.user_repository


def get_postgres_session_factory():
    return _app.state.postgres_session_factory


def get_redis_client():
    return _app.state.redis_client


def get_mongo_db():
    return _app.state.mongo_db
