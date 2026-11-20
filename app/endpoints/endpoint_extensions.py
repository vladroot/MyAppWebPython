"""Single entry point that wires up every endpoint group."""

from fastapi import FastAPI

from app.endpoints import database_info, health, products, watch


def map_application_endpoints(app: FastAPI) -> None:
    app.include_router(watch.router)
    app.include_router(products.router)
    app.include_router(health.router)
    app.include_router(database_info.router)