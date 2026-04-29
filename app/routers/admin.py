from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Store, User
from app.schemas import StoreCreate, StoreUpdate, StoreResponse, UserCreate, UserResponse
from app.dependencies import get_current_user, require_role
from app.utils import hash_password
from typing import List
import csv
import io

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/stores", response_model=StoreResponse, status_code=201)
def create_store(
    store: StoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "marketer"))
):
    existing = db.query(Store).filter(Store.store_id == store.store_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Store ID already exists")

    db_store = Store(**store.model_dump())
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store


@router.get("/stores", response_model=List[StoreResponse])
def list_stores(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Store).offset(skip).limit(limit).all()


@router.get("/stores/{store_id}", response_model=StoreResponse)
def get_store(
    store_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    store = db.query(Store).filter(Store.store_id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store


@router.patch("/stores/{store_id}", response_model=StoreResponse)
def update_store(
    store_id: str,
    updates: StoreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "marketer"))
):
    store = db.query(Store).filter(Store.store_id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(store, field, value)

    db.commit()
    db.refresh(store)
    return store


@router.delete("/stores/{store_id}")
def deactivate_store(
    store_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "marketer"))
):
    store = db.query(Store).filter(Store.store_id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    store.status = "inactive"
    db.commit()
    return {"message": f"Store {store_id} deactivated"}

@router.post("/stores/import")
def import_stores(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "marketer"))
):
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))

    created, updated, failed = 0, 0, []

    for i, row in enumerate(reader, start=2):
        try:
            store_id = row["store_id"]
            existing = db.query(Store).filter(Store.store_id == store_id).first()

            data = {
                "store_id": store_id,
                "name": row["name"],
                "store_type": row["store_type"],
                "status": row["status"],
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "address_street": row["address_street"],
                "address_city": row["address_city"],
                "address_state": row["address_state"],
                "address_postal_code": row["address_postal_code"],
                "address_country": row["address_country"],
                "phone": row["phone"],
                "services": row["services"],
                "hours_mon": row["hours_mon"],
                "hours_tue": row["hours_tue"],
                "hours_wed": row["hours_wed"],
                "hours_thu": row["hours_thu"],
                "hours_fri": row["hours_fri"],
                "hours_sat": row["hours_sat"],
                "hours_sun": row["hours_sun"],
            }

            if existing:
                for k, v in data.items():
                    setattr(existing, k, v)
                updated += 1
            else:
                db.add(Store(**data))
                created += 1

        except Exception as e:
            failed.append({"row": i, "error": str(e)})

    db.commit()

    return {
        "total": created + updated + len(failed),
        "created": created,
        "updated": updated,
        "failed": len(failed),
        "errors": failed
    }

@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    db_user = User(
        email=user.email,
        username=user.username,
        hash_password=hash_password(user.password),
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/users", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    return db.query(User).all()


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    updates: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in updates.items():
        if field in ("role", "is_active"):
            setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    return {"message": f"User {user_id} deactivated"}