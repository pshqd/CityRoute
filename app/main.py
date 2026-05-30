from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="CityRoute — Vehicle Routing Lite",
    version="0.1.0",
    description="Single-courier constrained routing research backend",
)

app.include_router(router, prefix="/api/v1")
