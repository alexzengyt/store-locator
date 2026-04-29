from math import cos, radians
from geopy.distance import geodesic
import requests
import jwt
import bcrypt
import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from collections import defaultdict
import threading
import redis as redis_client
import json


def calculate_bounding_box(lat: float, lon: float, radius_miles: float) -> dict:
    lat_delta = radius_miles / 69.0
    lon_delta = radius_miles / (69.0 * cos(radians(lat)))

    return {
        "min_lat": lat - lat_delta,
        "max_lat": lat + lat_delta,
        "min_lon": lon - lon_delta,
        "max_lon": lon + lon_delta,
    }


def calculate_distance_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    return geodesic((lat1, lon1), (lat2, lon2)).miles

_redis = redis_client.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

def geocode_address(address: str) -> tuple[float, float]:
    cache_key = f"geocode:{address}"
    
    cached = _redis.get(cache_key)
    if cached:
        data = json.loads(cached)
        return data["lat"], data["lon"]
    
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1}
    headers = {"User-Agent": "store-locator-app"}
    response = requests.get(url, params=params, headers=headers, timeout=10)
    results = response.json()
    
    if not results:
        raise ValueError(f"Could not geocode address: {address}")
    
    lat, lon = float(results[0]["lat"]), float(results[0]["lon"])
    
    _redis.setex(cache_key, 60 * 60 * 24 * 30, json.dumps({"lat": lat, "lon": lon}))
    
    return lat, lon

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15)))
    }
    return jwt.encode(payload, os.getenv("JWT_SECRET_KEY"), algorithm=os.getenv("JWT_ALGORITHM", "HS256"))


def create_refresh_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7)))
    }
    return jwt.encode(payload, os.getenv("JWT_SECRET_KEY"), algorithm=os.getenv("JWT_ALGORITHM", "HS256"))


def decode_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM", "HS256")])
        return payload.get("user_id")
    except Exception:
        return None

_rate_limit_store = defaultdict(list)
_lock = threading.Lock()

def check_rate_limit(ip: str, max_requests: int, window_seconds: int) -> bool:
    now = datetime.now(timezone.utc).timestamp()
    with _lock:
        timestamps = _rate_limit_store[ip]
        _rate_limit_store[ip] = [t for t in timestamps if now - t < window_seconds]
        if len(_rate_limit_store[ip]) >= max_requests:
            return False
        _rate_limit_store[ip].append(now)
        return True