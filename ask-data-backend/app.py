from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from datetime import datetime

from api.routes import router
from config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format
)

app = FastAPI(
    title="AskData API", 
    version="1.0.0",
    description="Intelligent Text-to-SQL API for Internal Bank Transfer System",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["AskData"])

@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "askdata-api"}

# Exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper logging."""
    logging.warning(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": datetime.utcnow().isoformat() + "Z"}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logging.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "timestamp": datetime.utcnow().isoformat() + "Z"}
    )

# Allow CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def main() -> None:
    """Entrypoint to invoke when this module is invoked on the remote server."""
    uvicorn.run(
        "app:app", 
        host=settings.api_host, 
        port=settings.api_port,
        reload=settings.debug_mode
    )

if __name__ == "__main__":
    main()