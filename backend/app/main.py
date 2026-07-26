from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routes import api_router
import app.models  # noqa: F401  (ensures models are registered on Base before create_all)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise AI Business Intelligence Platform API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://insight-flow-ai-indol.vercel.app",
        "https://insight-flow-jr8zcxq75-mahesh-b9c6.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    # For local/dev convenience. In production, use Alembic migrations instead.
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"service": settings.PROJECT_NAME, "status": "running", "docs": "/api/docs"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(api_router, prefix=settings.API_V1_PREFIX)
