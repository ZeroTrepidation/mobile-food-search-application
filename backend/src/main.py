from fastapi import FastAPI

from backend.src.domains.mobileFoodSearch.infrastructure.applicant_inmemory_repository import \
    ApplicantInMemoryRepository
from backend.src.domains.mobileFoodSearch.infrastructure.sf_gov_datasource import SODAClient

app = FastAPI()

DATASET_ID = "rqzj-sfat"  # SF food truck dataset
CHECK_INTERVAL = 3600  # seconds (1 hour)

soda_client = SODAClient()
applicant_repo = ApplicantInMemoryRepository(soda_client, DATASET_ID)


async def on_dataset_change(dataset_id: str):
    """Triggered when dataset changes."""
    await applicant_repo.refresh()


async def monitor_task():
    while True:
        await soda_client.check_for_updates(DATASET_ID, on_dataset_change)
        await asyncio.sleep(CHECK_INTERVAL)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

