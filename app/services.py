from sqlalchemy.orm import Session
from app.models import Store
from app.utils import calculate_bounding_box, calculate_distance_miles
from typing import Optional, List
from datetime import datetime


def search_stores(
    db: Session,
    latitude: float,
    longitude: float,
    radius_miles: float = 10,
    services: Optional[List[str]] = None,
    store_types: Optional[List[str]] = None,
    open_now: Optional[bool] = None
) -> List[dict]:

    # Step 1: bounding box pre-filter
    bbox = calculate_bounding_box(latitude, longitude, radius_miles)

    query = db.query(Store).filter(
        Store.status == "active",
        Store.latitude >= bbox["min_lat"],
        Store.latitude <= bbox["max_lat"],
        Store.longitude >= bbox["min_lon"],
        Store.longitude <= bbox["max_lon"],
    )

    # Step 2: store_type filter (OR logic)
    if store_types:
        query = query.filter(Store.store_type.in_(store_types))

    stores = query.all()

    # Step 3: calculate exact distance and apply radius filter
    results = []
    for store in stores:
        distance = calculate_distance_miles(latitude, longitude, store.latitude, store.longitude)
        if distance <= radius_miles:
            store_dict = {
                "store_id": store.store_id,
                "name": store.name,
                "store_type": store.store_type,
                "status": store.status,
                "latitude": store.latitude,
                "longitude": store.longitude,
                "address_street": store.address_street,
                "address_city": store.address_city,
                "address_state": store.address_state,
                "address_postal_code": store.address_postal_code,
                "address_country": store.address_country,
                "phone": store.phone,
                "services": store.services,
                "hours_mon": store.hours_mon,
                "hours_tue": store.hours_tue,
                "hours_wed": store.hours_wed,
                "hours_thu": store.hours_thu,
                "hours_fri": store.hours_fri,
                "hours_sat": store.hours_sat,
                "hours_sun": store.hours_sun,
                "distance_miles": round(distance, 2),
                "is_open_now": is_store_open(store),
            }

            # services filter (AND logic)
            if services:
                store_services = store.services.split("|") if store.services else []
                if not all(s in store_services for s in services):
                    continue

            # open_now filter
            if open_now is not None:
                if open_now and not store_dict["is_open_now"]:
                    continue

            results.append(store_dict)

    # Step 4: sort by distance
    results.sort(key=lambda x: x["distance_miles"])
    return results


def is_store_open(store: Store) -> bool:
    now = datetime.now()
    day_map = {0: "mon", 1: "tue", 2: "wed", 3: "thu", 4: "fri", 5: "sat", 6: "sun"}
    day_key = f"hours_{day_map[now.weekday()]}"
    hours = getattr(store, day_key)

    if not hours or hours.lower() == "closed":
        return False

    try:
        open_str, close_str = hours.split("-")
        open_h, open_m = map(int, open_str.split(":"))
        close_h, close_m = map(int, close_str.split(":"))
        current_minutes = now.hour * 60 + now.minute
        open_minutes = open_h * 60 + open_m
        close_minutes = close_h * 60 + close_m
        return open_minutes <= current_minutes < close_minutes
    except Exception:
        return False