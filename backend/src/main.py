import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from backend.src.domains.mobileFoodSearch.infrastructure.applicant_inmemory_repository import \
    ApplicantInMemoryRepository
from backend.src.domains.mobileFoodSearch.infrastructure.sf_gov_datasource import SODAClientDatasource
from backend.src.domains.mobileFoodSearch.application.soda_applicant_loader_service import SodaApplicantLoaderService
from backend.src.domains.mobileFoodSearch.application.applicant_service import ApplicantService


# Initialize repository and SODA-backed loader service.
applicant_repo = ApplicantInMemoryRepository()

SODA_DOMAIN = os.getenv("SODA_DOMAIN", "data.sfgov.org")
SODA_DATASET_ID = os.getenv("SODA_DATASET_ID", "rqzj-sfat")
soda = SODAClientDatasource(SODA_DOMAIN, SODA_DATASET_ID)

# Minimal mapping from Socrata row dict to a simple entity with a stable key.
class RowApplicant:
    def __init__(self, row: dict):
        # Use common Socrata field names; fall back gracefully
        self.locationId = row.get("locationid") or row.get("locationId") or ""
        self.name = row.get("Applicant") or row.get("applicant") or ""
        self.foodItems = row.get("FoodItems") or row.get("fooditems") or ""
        self.raw = row


def to_entity(row: dict) -> RowApplicant:
    return RowApplicant(row)

loader_service = SodaApplicantLoaderService(applicant_repo, soda, to_entity, interval_seconds=3600)
applicant_service = ApplicantService(applicant_repo)


@asynccontextmanager
async def lifespan(app: FastAPI):
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


@app.get("/applicants/{applicant_id}")
async def get_applicant_by_id(applicant_id: str):
    obj = applicant_service.get_applicant_by_id(applicant_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Applicant not found")

    # Map repository object (RowApplicant, domain Applicant, or dict) to a simple response
    if isinstance(obj, dict):
        return {
            "locationId": obj.get("locationid") or obj.get("locationId") or obj.get("id") or "",
            "name": obj.get("Applicant") or obj.get("applicant") or "",
            "foodItems": obj.get("FoodItems") or obj.get("fooditems") or "",
        }

    resp = {}
    if hasattr(obj, "locationId"):
        resp["locationId"] = getattr(obj, "locationId")
    if hasattr(obj, "name"):
        resp["name"] = getattr(obj, "name")
    if hasattr(obj, "foodItems"):
        resp["foodItems"] = getattr(obj, "foodItems")

    # Fallback: attempt to derive locationId from nested structures
    if "locationId" not in resp:
        try:
            loc_id = getattr(getattr(obj, "permit", None), "locationId", None) or getattr(obj, "id", None)
            if loc_id:
                resp["locationId"] = str(loc_id)
        except Exception:
            pass

    # Optionally include raw source data if present
    if hasattr(obj, "raw"):
        resp["raw"] = getattr(obj, "raw")

    return resp

