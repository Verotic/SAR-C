"""
SAR-C Backend - Search & Rescue with Copernicus
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import drift, data

settings = get_settings()

app = FastAPI(
    title="SAR-C API",
    description="Search & Rescue with Copernicus - Drift Prediction API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(drift.router, prefix="/api/drift", tags=["Drift Calculation"])
app.include_router(data.router, prefix="/api/data", tags=["Copernicus Data"])


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "operational",
        "service": "SAR-C API",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "copernicus_configured": bool(settings.copernicus_username),
        "cache_dir": str(settings.data_cache_dir)
    }
