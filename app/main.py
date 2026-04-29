from fastapi import FastAPI
from dotenv import load_dotenv
from app.database import engine, Base
from app.routers import stores, auth, admin


load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Store Locator API")
app.include_router(stores.router)
app.include_router(auth.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"message": "Store Locator API"}