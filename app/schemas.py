from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ─── Store Schemas ───────────────────────────────────────────

class StoreSearchRequest(BaseModel):
    address: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_miles: float = Field(default=10, le=100)
    services: Optional[List[str]] = None
    store_types: Optional[List[str]] = None
    open_now: Optional[bool] = None


class StoreResponse(BaseModel):
    store_id: str
    name: str
    store_type: str
    status: str
    latitude: float
    longitude: float
    address_street: Optional[str]
    address_city: Optional[str]
    address_state: Optional[str]
    address_postal_code: Optional[str]
    address_country: Optional[str]
    phone: Optional[str]
    services: Optional[str]
    hours_mon: Optional[str]
    hours_tue: Optional[str]
    hours_wed: Optional[str]
    hours_thu: Optional[str]
    hours_fri: Optional[str]
    hours_sat: Optional[str]
    hours_sun: Optional[str]
    distance_miles: Optional[float] = None
    is_open_now: Optional[bool] = None

    model_config = {"from_attributes": True}


class StoreCreate(BaseModel):
    store_id: str
    name: str
    store_type: str
    status: str = "active"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address_street: str
    address_city: str
    address_state: str
    address_postal_code: str
    address_country: str = "USA"
    phone: Optional[str] = None
    services: Optional[str] = None
    hours_mon: Optional[str] = None
    hours_tue: Optional[str] = None
    hours_wed: Optional[str] = None
    hours_thu: Optional[str] = None
    hours_fri: Optional[str] = None
    hours_sat: Optional[str] = None
    hours_sun: Optional[str] = None


class StoreUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    services: Optional[str] = None
    status: Optional[str] = None
    hours_mon: Optional[str] = None
    hours_tue: Optional[str] = None
    hours_wed: Optional[str] = None
    hours_thu: Optional[str] = None
    hours_fri: Optional[str] = None
    hours_sat: Optional[str] = None
    hours_sun: Optional[str] = None


# ─── Auth Schemas ────────────────────────────────────────────

class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    role: str = "viewer"


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str