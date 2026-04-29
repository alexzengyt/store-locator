from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import StoreSearchRequest
from app.services import search_stores
from app.utils import geocode_address, check_rate_limit

router = APIRouter(prefix="/api/stores", tags=["stores"])


@router.post("/search")
def search(request: Request, body: StoreSearchRequest, db: Session = Depends(get_db)):
    ip = request.client.host
    if not check_rate_limit(ip, max_requests=10, window_seconds=60):
        raise HTTPException(status_code=429, detail="Rate limit exceeded: 10 requests per minute")
    if not check_rate_limit(ip, max_requests=100, window_seconds=3600):
        raise HTTPException(status_code=429, detail="Rate limit exceeded: 100 requests per hour")

    if body.latitude is not None and body.longitude is not None:
        lat, lon = body.latitude, body.longitude
    elif body.postal_code:
        try:
            lat, lon = geocode_address(body.postal_code)
        except ValueError:
            raise HTTPException(status_code=400, detail="Could not geocode postal code")
    elif body.address:
        try:
            lat, lon = geocode_address(body.address)
        except ValueError:
            raise HTTPException(status_code=400, detail="Could not geocode address")
    else:
        raise HTTPException(status_code=400, detail="Provide latitude/longitude, postal_code, or address")

    results = search_stores(
        db=db,
        latitude=lat,
        longitude=lon,
        radius_miles=body.radius_miles,
        services=body.services,
        store_types=body.store_types,
        open_now=body.open_now,
    )

    return {
        "results": results,
        "count": len(results),
        "search_location": {"latitude": lat, "longitude": lon},
        "filters": {
            "radius_miles": body.radius_miles,
            "services": body.services,
            "store_types": body.store_types,
            "open_now": body.open_now,
        }
    }