from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, RefreshToken
from app.schemas import UserCreate, LoginRequest, TokenResponse, RefreshRequest
from app.utils import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from datetime import datetime, timedelta
import hashlib
import os

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hash_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    db_token = RefreshToken(
        token_hash=token_hash,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7)))
    )
    db.add(db_token)
    db.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh")
def refresh(request: RefreshRequest, db: Session = Depends(get_db)):
    user_id = decode_token(request.refresh_token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    token_hash = hashlib.sha256(request.refresh_token.encode()).hexdigest()
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash,
        RefreshToken.is_revoked == False
    ).first()

    if not db_token or db_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired or revoked")

    access_token = create_access_token(user_id)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(request: RefreshRequest, db: Session = Depends(get_db)):
    token_hash = hashlib.sha256(request.refresh_token.encode()).hexdigest()
    db_token = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if db_token:
        db_token.is_revoked = True
        db.commit()
    return {"message": "Logged out successfully"}