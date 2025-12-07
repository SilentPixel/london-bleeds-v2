# FastAPI application entry point
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pathlib import Path
from dotenv import load_dotenv
import traceback

# Load .env file from project root at application startup
# This ensures environment variables are available before any modules try to use them
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

from .config import settings
from .deps import get_db
from api.routes_health import router as health_router
from api.routes_debug import router as debug_router
from api.routes_debug_turns import router as debug_turns_router
from api.routes_memory import router as memory_router
from api.routes_play import router as play_router

app = FastAPI(title=settings.APP_NAME)

# Global exception handler to ensure all errors return JSON
from fastapi.exceptions import HTTPException as FastAPIHTTPException

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions and return JSON error response"""
    # Don't override FastAPI's HTTPException handler
    if isinstance(exc, FastAPIHTTPException):
        raise exc
    
    error_trace = traceback.format_exc()
    print(f"Unhandled exception in {request.url.path}:\n{error_trace}", flush=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)}
    )

# Add CORS middleware to allow React dev server
app.add_middleware(
    CORSMiddleware,
    # Allow both localhost and 127.0.0.1 for the React dev server
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(debug_router, prefix="/debug", tags=["debug"])
app.include_router(debug_turns_router, prefix="/debug/turns", tags=["debug", "turns"])
app.include_router(memory_router, tags=["memory"])
app.include_router(play_router, tags=["play"])
