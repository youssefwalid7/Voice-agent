from fastapi import FastAPI, status
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.logging_config import configure_logging
from app.database import create_pool, close_pool, get_pool
from app.config.settings import settings
from app.api.routes import voice_agent
# Use the centralized logging configuration
logger = configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await create_pool()
        logger.info("Database connection pool initialized")
        yield
    finally:
        logger.info("Closing database connection pool")
        await close_pool()

app = FastAPI(
    lifespan=lifespan,
    title="wittify voice assistant",
    version="1.0.0",
)

# Production-grade CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # TODO Add frontend url only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
    max_age=300
)

# Include routers with versioning
app.include_router(
    voice_agent.router,
    prefix="/api/v1",
    tags=["API Integration"],
)

# Enhanced health check endpoint
@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["System Health"],
    summary="System Health Check",
    response_description="System Health Status"
)
async def health_check():
    """Comprehensive health check for critical services"""
    health_status = {"status": "healthy", "services": {}}
    try:
        pool = get_pool()
        async with pool.acquire(timeout=5) as conn:
            await conn.execute("SELECT 1")
            health_status["services"]["database"] = "ok"
            
    except Exception as e:
        logger.critical(f"Database health check failed: {str(e)}", exc_info=True)
        health_status["status"] = "degraded"
        health_status["services"]["database"] = {
            "error": "Database connection failed",
            "details": str(e)
        }
        
    if health_status["status"] != "healthy":
        return JSONResponse(
            content=health_status,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return health_status