import asyncio
import logging
from contextlib import asynccontextmanager
from typing import List


from dependency_injector.wiring import inject
from fastapi import FastAPI, HTTPException

from backend.app.adapters.memory import InMemoryFoodProviderRepository
from backend.app.adapters.sfgov_client import SFGovFoodProviderClient
from backend.app.domain.foodprovider_specifications import HasPermitStatus, LikeName, LikeStreetName, \
    ClosestToPointSpecification
from backend.app.domain.models import PermitStatus, FoodProvider
from backend.app.task.task_bus import AsyncTaskBus

logging.basicConfig(level=logging.INFO)

repository = InMemoryFoodProviderRepository()
sfgov_datasource = SFGovFoodProviderClient(repository)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting application...")

    bus = AsyncTaskBus()
    bus.add_task(
        name="sf_gov_periodic_update",
        interval_fn=sfgov_datasource.get_interval,
        task_fn=sfgov_datasource.periodic_task
    )

    try:
        logging.info("Running initial data sync before startup...")
        await asyncio.wait_for(sfgov_datasource.periodic_task(), timeout=60)
        logging.info("Initial data sync completed.")
    except Exception as e:
        logging.exception(f"Initial data sync failed: {e}")
        # Abort startup by re-raising so FastAPI doesn't start
        raise

    logging.info("Starting AsyncTaskBus...")
    bus_task = asyncio.create_task(bus.start())

    yield
    logging.info("Stopping AsyncTaskBus...")
    await bus.stop()
    if not bus_task.done():
        bus_task.cancel()
        try:
            await bus_task
        except asyncio.CancelledError:
            pass

    logging.info("Application shutdown complete.")

app = FastAPI(lifespan=lifespan)

BASE_API_PATH = "/api/v1"

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get(BASE_API_PATH + "/food-providers/name/{name}", response_model=List[FoodProvider])
async def get_food_providers(name: str = "", status: str = ""):
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

    items = repository.get_by_spec(spec)
    return items


@app.get(BASE_API_PATH + "/food-providers/street/{street}", response_model=List[FoodProvider])
@inject
async def get_food_providers(street: str = ""):
    if street == "":
        raise HTTPException(status_code=400, detail="Street cannot be empty")
    spec = LikeStreetName(street)

    print(street)

    items = repository.get_by_spec(spec)
    return items


@app.get(BASE_API_PATH + "/food-providers/closest", response_model=List[FoodProvider])
@inject
async def get_n_closest_providers(lng: str, lat: str, status: str = "APPROVED", limit: str = "5"):
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

    if status != "":
        try:
            permit_status = PermitStatus(status.upper())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"'{status}' is not a valid PermitStatus"
            )
        spec &= HasPermitStatus(permit_status)

    items = repository.get_by_spec(spec)
    return items

