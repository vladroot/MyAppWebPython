"""POST /addproduct and GET /getproducts."""

import json
import sqlite3
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select

from app.config import DatabaseOptions
from app.dependencies import get_message_log, get_options, get_postgres_session_factory, get_redis_client
from app.models import Product
from app.schemas import ApiResponse, ProductResponse
from app.services.message_log import ServerMessageLog

router = APIRouter(tags=["Products"])

PRODUCTS_CACHE_KEY = "products:all"
PRODUCTS_CACHE_TTL = timedelta(minutes=5)


@router.post("/addproduct")
async def add_product(
    options: DatabaseOptions = Depends(get_options),
    message_log: ServerMessageLog = Depends(get_message_log),
    session_factory = Depends(get_postgres_session_factory),
    redis = Depends(get_redis_client),
):
    product = Product(name="TestProduct", price=10.0, stock=20)

    async with session_factory() as session:
        session.add(product)
        await session.commit()
        await session.refresh(product)

    # Invalidate the cached product list so the next read rebuilds it.
    if redis:
        try:
            await redis.delete(PRODUCTS_CACHE_KEY)
        except Exception:
            pass  # cache invalidation failure must not fail the endpoint

    response = ApiResponse(
        status="success",
        message="added new product",
        timestamp=datetime.utcnow(),
    )
    message_log.add(response.model_dump_json())
    return JSONResponse(status_code=201, content=response.model_dump(mode="json"))


@router.get("/getproducts")
async def get_products(
    options: DatabaseOptions = Depends(get_options),
    message_log: ServerMessageLog = Depends(get_message_log),
    session_factory = Depends(get_postgres_session_factory),
    redis = Depends(get_redis_client),
):
    # Cache-aside: serve the stored list when Redis has it, otherwise read PostgreSQL
    # and refresh the entry. A broken cache must never fail the endpoint.
    cached_products = None
    if redis:
        try:
            cached_value = await redis.get(PRODUCTS_CACHE_KEY)
            if cached_value:
                cached_products = json.loads(cached_value)
        except Exception:
            cached_products = None

    if cached_products is not None:
        if len(cached_products) == 0:
            response = ApiResponse(
                status="success",
                message="no products yet",
                timestamp=datetime.utcnow(),
            )
            message_log.add(response.model_dump_json())
            return JSONResponse(status_code=200, content=response.model_dump(mode="json"))

        message_log.add(json.dumps(cached_products))
        return JSONResponse(status_code=200, content=cached_products)

    async with session_factory() as session:
        result = await session.execute(
            select(Product).order_by(Product.name)
        )
        products = result.scalars().all()

    payload = [
        ProductResponse(
            id=p.id,
            name=p.name,
            price=float(p.price),
            stock=p.stock,
        )
        for p in products
    ]

    if redis:
        try:
            await redis.set(
                PRODUCTS_CACHE_KEY,
                json.dumps([p.model_dump() for p in payload]),
                ex=int(PRODUCTS_CACHE_TTL.total_seconds()),
            )
        except Exception:
            pass  # cache write failure must not fail the endpoint

    if len(payload) == 0:
        response = ApiResponse(
            status="success",
            message="no products yet",
            timestamp=datetime.utcnow(),
        )
        message_log.add(response.model_dump_json())
        return JSONResponse(status_code=200, content=response.model_dump(mode="json"))

    message_log.add(json.dumps([p.model_dump() for p in payload]))
    return JSONResponse(status_code=200, content=[p.model_dump() for p in payload])
