from sqlalchemy import Column, String, Float, Integer, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Store(Base):
    __tablename__ = "stores"

    store_id = Column(String(10), primary_key=True)
    name = Column(String(255), nullable=False)
    store_type = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="active")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address_street = Column(String(255))
    address_city = Column(String(100))
    address_state = Column(String(2))
    address_postal_code = Column(String(10), index=True)
    address_country = Column(String(3))
    phone = Column(String(20))
    services = Column(String(255))
    hours_mon = Column(String(20))
    hours_tue = Column(String(20))
    hours_wed = Column(String(20))
    hours_thu = Column(String(20))
    hours_fri = Column(String(20))
    hours_sat = Column(String(20))
    hours_sun = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    hash_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="viewer")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    refresh_tokens = relationship("RefreshToken", back_populates="user")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token_hash = Column(String(255), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="refresh_tokens")