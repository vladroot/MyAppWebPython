"""GET /watch and GET /json."""

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse, JSONResponse

from app.dependencies import get_message_log, get_save_load
from app.services.message_log import ServerMessageLog
from app.services.save_load import SaveLoadController

router = APIRouter(tags=["Watch"])


@router.get("/watch")
async def get_watch(message_log: ServerMessageLog = Depends(get_message_log)):
    messages = message_log.snapshot()
    if not messages:
        return JSONResponse(status_code=200, content=["Nothing here yet"])
    return JSONResponse(status_code=200, content=messages)


@router.get("/json")
async def get_json(
    save_load: SaveLoadController = Depends(get_save_load),
    message_log: ServerMessageLog = Depends(get_message_log),
):
    json_str = save_load.do_work()
    message_log.add(json_str)
    return PlainTextResponse(content=json_str, media_type="application/json")
