"""Version probes for the three datastores: GET /postgres, GET /mongo, GET /sqlite."""

import sqlite3
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse, JSONResponse
from sqlalchemy import text

from app.config import DatabaseOptions
from app.database import get_sqlite_connection_string
from app.dependencies import get_mongo_db, get_message_log, get_options, get_postgres_session_factory
from app.services.message_log import ServerMessageLog
from app.schemas import DatabaseVersionResponse, MongoProbeResponse

router = APIRouter(tags=["Databases"])

POSTGRES_VERSION_QUERY = 'SELECT version() as "Value"'


@router.get("/postgres")
async def get_postgres(
    message_log: ServerMessageLog = Depends(get_message_log),
    session_factory = Depends(get_postgres_session_factory),
):
    async with session_factory() as session:
        result = await session.execute(text(POSTGRES_VERSION_QUERY))
        version = result.scalar_one_or_none()

    response = DatabaseVersionResponse(
        database="postgresql",
        version=str(version) if version else None,
        timestamp=datetime.now(),
    )
    message_log.add(response.model_dump_json())
    return JSONResponse(status_code=200, content=response.model_dump(mode="json"))


@router.get("/mongo")
async def get_mongo(
    message_log: ServerMessageLog = Depends(get_message_log),
    mongo_db = Depends(get_mongo_db),
):
    try:
        admin_db = mongo_db.client.get_database("admin")
        command_result = await admin_db.command("buildInfo")
        mongo_version = str(command_result.get("version", ""))

        response = MongoProbeResponse.ok(mongo_version)
        text = response.model_dump_json(indent=2)
        message_log.add(text)
        return PlainTextResponse(content=text, media_type="application/json")
    except Exception as ex:
        response = MongoProbeResponse.error(str(ex))
        text = response.model_dump_json(indent=2)
        message_log.add(text)
        return PlainTextResponse(content=text, media_type="application/json")


@router.get("/sqlite")
async def get_sqlite(
    options: DatabaseOptions = Depends(get_options),
    message_log: ServerMessageLog = Depends(get_message_log),
):
    conn_str = get_sqlite_connection_string(options)
    if not conn_str:
        return PlainTextResponse(
            content="SqliteConnnection not set", media_type="text/plain"
        )

    conn = sqlite3.connect(conn_str)
    try:
        cursor = conn.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
    finally:
        conn.close()

    response = DatabaseVersionResponse(
        database="sqlite",
        version=str(version),
        timestamp=datetime.utcnow(),
    )
    message_log.add(response.model_dump_json())
    return JSONResponse(status_code=200, content=response.model_dump(mode="json"))
