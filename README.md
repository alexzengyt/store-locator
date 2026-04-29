# Store Locator API

A production-ready Store Locator API service for a multi-location retail business. Supports public store search and secure internal store management with role-based access control.

---

## Framework & Tech Stack

| Component | Choice |
|---|---|
| Web Framework | FastAPI |
| Database | PostgreSQL + SQLAlchemy |
| Cache | Redis |
| CSV Processing | Python built-in `csv` module |
| Authentication | JWT (PyJWT) |
| Password Hashing | bcrypt |
| Distance Calculation | geopy (Haversine) |
| Deployment | Render |

---

## Local Setup

### Prerequisites

- Python 3.10+
- PostgreSQL
- Redis

### Installation

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```
DATABASE_URL=postgresql://username:password@localhost:5432/store_locator
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Run Locally

```bash
fastapi dev app/main.py
```

### Seed Database

```bash
python seed.py
```

---

## API Documentation

Interactive docs available at `/docs` (Swagger UI).

### Public Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/stores/search` | Search stores by coordinates, address, or postal code |

**Search supports:**
- Latitude / Longitude
- Address string (geocoded via Nominatim)
- Postal code (geocoded via Nominatim)

**Filters:**
- `radius_miles` (default: 10, max: 100)
- `services[]` (AND logic)
- `store_types[]` (OR logic)
- `open_now` (boolean)

### Auth Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/login` | Login, returns access + refresh token |
| POST | `/api/auth/refresh` | Get new access token |
| POST | `/api/auth/logout` | Revoke refresh token |

### Admin Endpoints (Authenticated)

| Method | Endpoint | Roles | Description |
|---|---|---|---|
| GET | `/api/admin/stores` | All | List stores (paginated) |
| POST | `/api/admin/stores` | Admin, Marketer | Create store |
| GET | `/api/admin/stores/{store_id}` | All | Get store details |
| PATCH | `/api/admin/stores/{store_id}` | Admin, Marketer | Partial update store |
| DELETE | `/api/admin/stores/{store_id}` | Admin, Marketer | Deactivate store (soft delete) |
| POST | `/api/admin/stores/import` | Admin, Marketer | Bulk CSV import (upsert) |
| GET | `/api/admin/users` | Admin | List users |
| POST | `/api/admin/users` | Admin | Create user |
| PUT | `/api/admin/users/{user_id}` | Admin | Update user role/status |
| DELETE | `/api/admin/users/{user_id}` | Admin | Deactivate user |

---

## Authentication Flow

1. `POST /api/auth/login` with email and password
2. Receive `access_token` (15 min) and `refresh_token` (7 days)
3. Include `Authorization: Bearer <access_token>` in all protected requests
4. When access token expires, call `POST /api/auth/refresh` with refresh token
5. On logout, call `POST /api/auth/logout` to revoke refresh token

---

## Distance Calculation

Uses **Bounding Box Pre-filter + Haversine Formula**:

1. Calculate a bounding box around the search location
2. SQL `WHERE` clause filters stores within the box
3. Exact distances calculated using `geopy.distance.geodesic`
4. Results filtered by radius and sorted by distance (nearest first)

---

## Rate Limiting

Public search endpoint is rate limited:
- 10 requests per minute per IP
- 100 requests per hour per IP
- Returns HTTP 429 when exceeded

---

## Caching

- Geocoding results cached in Redis (TTL: 30 days)

---

## Test Credentials

| Role | Email | Password |
|---|---|---|
| Admin | admin@test.com | AdminTest123! |
| Marketer | marketer@test.com | MarketerTest123! |
| Viewer | viewer@test.com | ViewerTest123! |

---

## Run Tests

```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

Coverage target: 60% minimum (current: 71%)

---

## Deployment

- **Platform**: Render
- **URL**: https://store-locator-uzm2.onrender.com/
- **API Docs**: https://store-locator-uzm2.onrender.com/docs
- **Database**: Render PostgreSQL (1000 stores loaded)
- **Cache**: Render Key Value (Redis)

---

## Project Structure

```
project/
├── app/
│   ├── main.py          # FastAPI app entry point
│   ├── database.py      # Database connection
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── services.py      # Business logic
│   ├── dependencies.py  # Auth dependencies
│   ├── utils.py         # Helper functions
│   └── routers/
│       ├── auth.py      # Auth endpoints
│       ├── stores.py    # Public search endpoints
│       └── admin.py     # Admin endpoints
├── tests/
│   ├── test_utils.py
│   └── test_endpoints.py
├── seed.py              # Database seed script
├── requirements.txt
├── Procfile
└── .env
```
