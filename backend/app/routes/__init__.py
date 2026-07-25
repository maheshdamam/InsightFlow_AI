from fastapi import APIRouter

from app.routes import auth, datasets, analytics, ai, reports, admin

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(datasets.router)
api_router.include_router(analytics.router)
api_router.include_router(ai.router)
api_router.include_router(reports.router)
api_router.include_router(admin.router)
