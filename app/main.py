"""FastAPI application entry point (mirrors C# Program.cs)."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import DatabaseOptions, DefaultValueModels, FeatureOptions, SaveLoadModel
from app import database as db
from app.database import close_connections, init_mongo, init_postgres, init_redis
from app.dependencies import bind_app
from app.endpoints.endpoint_extensions import map_application_endpoints
from app.repositories.user_repository import UserRepository
from app.services.message_log import ServerMessageLog
from app.services.save_load import SaveLoadController


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    options = DatabaseOptions()

    # Default value models (mirrors appsettings.json FeatureOptions)
    default_models = DefaultValueModels(
        save_load_model=SaveLoadModel(),
        bool_datas=[
            # From appsettings.json DefaultValueModels.BoolDatas
            __import__("app.config", fromlist=["BoolData"]).BoolData(value=True),
            __import__("app.config", fromlist=["BoolData"]).BoolData(value=False),
            __import__("app.config", fromlist=["BoolData"]).BoolData(value=False),
            __import__("app.config", fromlist=["BoolData"]).BoolData(value=True),
            __import__("app.config", fromlist=["BoolData"]).BoolData(value=True),
            __import__("app.config", fromlist=["BoolData"]).BoolData(value=False),
            __import__("app.config", fromlist=["BoolData"]).BoolData(value=True),
            __import__("app.config", fromlist=["BoolData"]).BoolData(value=False),
            __import__("app.config", fromlist=["BoolData"]).BoolData(value=True),
            __import__("app.config", fromlist=["BoolData"]).BoolData(value=True),
        ],
    )

    await init_postgres(options)
    await init_mongo(options)
    await init_redis(options)

    # Attach services to app state for use in endpoints via dependency injection
    app.state.options = options
    app.state.mongo_db = db.mongo_db
    app.state.postgres_session_factory = db.postgres_session_factory
    app.state.redis_client = db.redis_client
    app.state.feature_options = FeatureOptions(default_value_models=default_models)
    app.state.message_log = ServerMessageLog()
    app.state.save_load = SaveLoadController(default_models)
    app.state.user_repository = UserRepository(app.state.mongo_db)

    yield

    # Shutdown
    await close_connections()


app = FastAPI(title="MyAppWeb", lifespan=lifespan)

bind_app(app)

map_application_endpoints(app)
