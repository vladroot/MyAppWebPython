"""Database connections and session factories for PostgreSQL, SQLite, MongoDB, and Redis."""

from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from redis.asyncio import ConnectionPool, Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import DatabaseOptions
from app.models import Base

# These are initialised in main.py during application startup.
postgres_engine = None
postgres_session_factory: Optional[async_sessionmaker[AsyncSession]] = None
mongo_client: Optional[AsyncIOMotorClient] = None
mongo_db: Optional[AsyncIOMotorDatabase] = None
redis_client: Optional[Redis] = None
redis_pool: Optional[ConnectionPool] = None


async def init_postgres(options: DatabaseOptions) -> None:
    global postgres_engine, postgres_session_factory
    postgres_engine = create_async_engine(options.postgres_connection, echo=False)
    # Create all tables defined on SQLAlchemy models (Products, Users, …).
    # The original project omitted its Migrations/ folder, so we create
    # schema directly on startup instead of running Alembic.
    async with postgres_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    postgres_session_factory = async_sessionmaker(
        postgres_engine, expire_on_commit=False
    )


async def init_mongo(options: DatabaseOptions) -> None:
    global mongo_client, mongo_db
    mongo_client = AsyncIOMotorClient(options.mongo_connection)
    mongo_db = mongo_client[options.mongo_db]


async def init_redis(options: DatabaseOptions) -> None:
    global redis_pool, redis_client
    if not options.is_redis_configured:
        return
    try:
        redis_pool = ConnectionPool.from_url(options.redis_connection, decode_responses=True)
        redis_client = Redis(connection_pool=redis_pool)
    except Exception as exc:  # noqa: BLE001
        # redis-py requires a redis:// URL; the provided string may be a
        # StackExchange.Redis-style connection string. Redis is optional, so
        # disable caching instead of crashing application startup.
        print(f"WARNING: could not initialise Redis from REDIS_CONNECTION: {exc}")
        print("WARNING: Redis caching disabled; cache operations will be no-ops.")
        redis_pool = None
        redis_client = None


async def close_connections() -> None:
    global redis_client, redis_pool, mongo_client, postgres_engine
    if redis_client:
        await redis_client.close()
    if redis_pool:
        await redis_pool.disconnect()
    if mongo_client:
        mongo_client.close()
    if postgres_engine:
        await postgres_engine.dispose()


def get_sqlite_connection_string(options: DatabaseOptions) -> str:
    """Return the SQLite connection string (used directly by sqlite3)."""
    return options.sqlite_connection