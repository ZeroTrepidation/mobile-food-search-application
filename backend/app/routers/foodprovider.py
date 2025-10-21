from typing import List, Annotated

from fastapi import APIRouter, HTTPException, Depends
from pydantic import ValidationError, ConfigDict

from app.dependencies import get_repository
from app.domain.foodprovider_specifications import HasPermitStatus, LikeStreetName, LikeName, \
    ClosestToPointSpecification
from app.domain.models import PermitStatus, FoodProvider, Coordinate
from app.domain.ports import FoodProviderRepository
from humps import camelize

router = APIRouter(
    prefix="/api/v1/food-providers",
    dependencies=[Depends(get_repository)],
)


def to_camel(string: str) -> str:
    return camelize(string)

class FoodProviderResponse(FoodProvider):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,  # Allow instantiation by either snake_case or camelCase
    )

@router.get(
    "/name/{name}",
    response_model=List[FoodProviderResponse],
    summary="Search for food providers by name",
    description=("Search for food providers by name and optionally by permit status. "
                 "Status must be one of APPROVED, REJECTED, PENDING, or SUSPEND.")
)
async def get_food_providers(repository: Annotated[FoodProviderRepository, Depends(get_repository)], name: str = "",
                             status: str = ""):
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


@router.get("/street/{street}", response_model=List[FoodProviderResponse])
async def get_food_providers(repository: Annotated[FoodProviderRepository, Depends(get_repository)], street: str = ""):
    if street == "":
        raise HTTPException(status_code=400, detail="Street cannot be empty")
    spec = LikeStreetName(street)

    print(street)

    items = repository.get_by_spec(spec)
    return items


@router.get("/closest", response_model=List[FoodProviderResponse])
async def get_n_closest_providers(repository: Annotated[FoodProviderRepository, Depends(get_repository)], lng: str,
                                  lat: str, status: str = "APPROVED", limit: str = "5"):
    try:
        limit_int = int(limit)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail='Limit must be an integer'
        )

    try:
        coord = Coordinate(longitude=lng, latitude=lat)
    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail=e.errors()[0]["msg"]
        )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=ValueError.args[0]
        )

    spec = ClosestToPointSpecification(coord, limit_int)

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
