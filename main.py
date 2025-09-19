import os
from contextlib import asynccontextmanager

import sentry_sdk
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from src.config.database import create_tables
from src.routers import auth, inventory

# Load environment variables from .env file
load_dotenv()


# Configure Sentry for error tracking
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[
        FastApiIntegration(),
        SqlalchemyIntegration(),
    ],
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables (only if DATABASE_URL is configured)
    database_url = os.getenv("DATABASE_URL")
    if database_url and not database_url.startswith("postgresql://user:password@localhost"):
        await create_tables()
    else:
        print("⚠️  Skipping database initialization - Configure DATABASE_URL for production")
    yield
    # Shutdown: Clean up resources if needed


# Create FastAPI app instance
app = FastAPI(
    title="API Auth Gateway",
    description="API Gateway que proporciona acceso autenticado a la API de inventario de activos",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS for Railway deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(inventory.router, prefix="/inventario", tags=["Inventory"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "API Auth Gateway",
        "status": "active",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {"status": "healthy"}