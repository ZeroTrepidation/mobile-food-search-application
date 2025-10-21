import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends

from app.dependencies import get_repository, initialize, shutdown
from app.routers import foodprovider

logging.basicConfig(level=logging.INFO, force=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialize()
    yield
    await shutdown()


app = FastAPI(
    lifespan=lifespan,
    dependencies=[Depends(get_repository)],
    title="Mobile Food Search API",
    description="A REST API for searching for mobile food providers. Currently limited to the San Francisco Food "
                "Authority data set.",
    version="0.1.0",
    docs_url="/api/docs",
    contact={
        "url": "https://github.com/ZeroTrepidation/mobile-food-search-application", "name": "Seth Tummillo"
    },
)

app.include_router(foodprovider.router)


@app.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "ok"}
