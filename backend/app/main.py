import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends

from backend.app.dependencies import get_repository, initialize, shutdown
from backend.app.routers import foodproviders

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialize()
    yield
    await shutdown()


app = FastAPI(lifespan=lifespan, dependencies=[Depends(get_repository)])

app.include_router(foodproviders.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
