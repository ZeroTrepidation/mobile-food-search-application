import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from typing import Any, List

from fastapi.encoders import jsonable_encoder

from .mobileFoodSearch import *
from .mobileFoodSearch.domain.foodprovider import HasPermitStatus, LikeName, ClosestToPointSpecification, LikeStreetName
from .mobileFoodSearch.domain.permit import PermitStatus
from .mobileFoodSearch.application.app_context import ApplicationContext

app_ctx: ApplicationContext | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global app_ctx
    soda = SODAClientDatasource("data.sfgov.org", "rqzj-sfat")
    foodprovider_repo = FoodproviderInMemoryRepository()
    try:
        app_ctx = ApplicationContext(repository=foodprovider_repo, datasource=soda, interval_seconds=3600)
    except Exception as ex:
        print(ex)
        raise
    # Ensure initial data is loaded before serving any requests
    await app_ctx.load_once()
    # Start background refresh (no-op in test env without running loop)
    app_ctx.start()
    yield
    await app_ctx.stop()
    app_ctx = None


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


BASE_API_PATH = "/api/v1"


@app.get(BASE_API_PATH + "/food-providers/name/{name}")
async def get_food_providers(name: str = "", status: str = "") -> List[dict]:
    if name == "":
        raise HTTPException(status_code=400, detail="Name cannot be empty")

    spec = LikeName(name)

    if status != "":
        try:
            permit_status = PermitStatus(status.upper())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"'{status}' is not a valid PermitStatus"
            )
        spec &= HasPermitStatus(permit_status)

    items = app_ctx.repository.get_by_spec(spec)
    return [p.to_dict() for p in items]


@app.get(BASE_API_PATH + "/food-providers/street/{street}")
async def get_food_providers(street: str = "") -> List[dict]:
    if street == "":
        raise HTTPException(status_code=400, detail="Street cannot be empty")
    spec = LikeStreetName(street)

    print(street)

    items = app_ctx.repository.get_by_spec(spec)
    return [jsonable_encoder(p) for p in items]


@app.get(BASE_API_PATH + "/food-providers/closest")
async def get_n_closest_providers(lng: str, lat: str, status: str = "APPROVED", limit: str = "5") -> List[dict]:
    if lng == "" or lat == "":
        raise HTTPException(status_code=400, detail="Long/Lat cannot be empty")

    try:
        long_float = float(lng)
        lat_float = float(lat)
        limit = int(limit)

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"'{lng}' is not a valid float"
        )

    spec = ClosestToPointSpecification(lat_float, long_float, limit)

    items = app_ctx.repository.get_by_spec(spec)
    return [jsonable_encoder(p) for p in items]
