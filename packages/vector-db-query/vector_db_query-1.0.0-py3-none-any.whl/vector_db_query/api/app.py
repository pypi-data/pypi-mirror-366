"""FastAPI application for Vector DB Query API endpoints."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from ..utils.logger import get_logger

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Vector DB Query API",
    description="API endpoints for Vector DB Query system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Import and include routers
from .webhooks import fireflies

app.include_router(fireflies.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Vector DB Query API",
        "version": "1.0.0",
        "endpoints": {
            "webhooks": {
                "fireflies": "/api/webhooks/fireflies",
                "fireflies_status": "/api/webhooks/fireflies/status",
                "fireflies_test": "/api/webhooks/fireflies/test"
            }
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


def run_api(host: str = "0.0.0.0", port: int = 8000):
    """Run the API server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
    """
    logger.info(f"Starting API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_api()