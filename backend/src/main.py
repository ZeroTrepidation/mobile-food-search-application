import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from typing import Any, List

from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from .mobileFoodSearch import *
from .mobileFoodSearch.domain.foodprovider import HasPermitStatus, LikeName, ClosestToPointSpecification
from .mobileFoodSearch.domain.permit import PermitStatus

# Initialize repository and SODA-backed loader service.
foodprovider_repo = FoodproviderInMemoryRepository()

SODA_DOMAIN = os.getenv("SODA_DOMAIN", "data.sfgov.org")
SODA_DATASET_ID = os.getenv("SODA_DATASET_ID", "rqzj-sfat")
SODA_BASE_URL_OVERRIDE = os.getenv("SODA_BASE_URL_OVERRIDE")
soda = SODAClientDatasource(SODA_DOMAIN, SODA_DATASET_ID, base_url_override=SODA_BASE_URL_OVERRIDE)


loader_service = None
food_provider_search = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        loader_service = SodaApplicantLoaderService(foodprovider_repo, soda, interval_seconds=3600)
        food_provider_search = FoodProviderSearchService(foodprovider_repo)
    except Exception as ex:
        print(ex)
        raise
    loader_service.start()
    yield
    await loader_service.stop()

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
            permit_status = PermitStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"'{status}' is not a valid PermitStatus"
            )
        spec &= HasPermitStatus(permit_status)

    items = foodprovider_repo.get_by_spec(spec)
    return [jsonable_encoder(p) for p in items]


@app.get("/food-providers/street/{street}")
async def get_food_providers(street: str = "") -> List[dict]:
    if street == "":
        raise HTTPException(status_code=400, detail="Street cannot be empty")
    spec = LikeName(street)

    items = foodprovider_repo.get_by_spec(spec)
    return [jsonable_encoder(p) for p in items]


@app.get("/food-providers/closest")
async def get_n_closest_providers(long: str, lat: str, status: str = "APPROVED", limit: str = "5") -> List[dict]:
    if long == "" or lat == "":
        raise HTTPException(status_code=400, detail="Long/Lat cannot be empty")

    try:
        long_float = float(long)
        lat_float = float(lat)
        limit = int(limit)

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"'{long}' is not a valid float"
        )

    spec = ClosestToPointSpecification(long_float, lat_float, limit)

    items = foodprovider_repo.get_by_spec(spec)
    return [jsonable_encoder(p) for p in items]