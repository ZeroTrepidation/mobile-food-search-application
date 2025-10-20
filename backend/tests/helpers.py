from datetime import datetime, timezone, timedelta

from backend.app.domain.models import PermitStatus, Permit, FoodProvider, Coordinate


def make_permit(status: PermitStatus | str = PermitStatus.APPROVED,
                exp_delta_days: int | None = None) -> Permit:
    now = datetime.now(timezone.utc)
    expiration = None
    if exp_delta_days is not None:
        expiration = now + timedelta(days=exp_delta_days)
    return Permit(permitStatus=status, permitID="P-1", approvalDate=now, recievedDate=now, expirationDate=expiration)


def make_provider(
        location_id: str,
        name: str = "Test Truck",
        food_items: str = "tacos, soda",
        permit: Permit = make_permit(),
        longitude: float | None = 10.0,
        latitude: float | None = 10.0,
        address: str = "1 Main St",
):
    return FoodProvider(
        location_id=location_id,
        name=name,
        food_items=food_items,
        permit=permit,
        coord=Coordinate(latitude=latitude, longitude=longitude),
        location_description=None,
        blocklot=None,
        block=None,
        lot=None,
        cnn=None,
        address=address,
    )


def general_mock_providers():
    a = make_provider("A", name="Truly", address="620 Mission St", latitude=1.0, longitude=2.0,
                      permit=make_permit(PermitStatus.APPROVED))
    b = make_provider("B", name="Truly", address="Columbia Ave", latitude=50.0, longitude=50.0,
                      permit=make_permit(PermitStatus.APPROVED))
    c = make_provider("C", name="C", address="120 Mission St", latitude=-60.0, longitude=-60.0,
                      permit=make_permit(PermitStatus.EXPIRED))
    d = make_provider("D", name="D", address="120 Test St", latitude=-64.0, longitude=-70.0,
                      permit=make_permit(PermitStatus.EXPIRED))
    e = make_provider("E", name="E", address="120 Test St", latitude=-80.0, longitude=-80.0,
                      permit=make_permit(PermitStatus.EXPIRED))
    return [a, b, c, d, e]
