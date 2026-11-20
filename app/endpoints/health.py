"""GET /health — polled by the healthcheck in compose.yaml."""

from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.config import DatabaseOptions
from app.dependencies import get_message_log, get_options
from app.services.message_log import ServerMessageLog
from app.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health")
async def get_health(
    options: DatabaseOptions = Depends(get_options),
    message_log: ServerMessageLog = Depends(get_message_log),
) -> JSONResponse:
    error: Optional[str] = options.validate()

    if error:
        response = HealthResponse.unhealthy(error, options.missing_keys)
        message_log.add(response.model_dump_json())
        return JSONResponse(status_code=503, content=response.model_dump(mode="json"))

    healthy = HealthResponse.healthy()
    message_log.add(healthy.model_dump_json())
    return JSONResponse(status_code=200, content=healthy.model_dump(mode="json"))
