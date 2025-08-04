"""API server command for CLI."""

import click
import asyncio
from typing import Optional

from ...api import run_api as run_api_server
from ...utils.logger import get_logger

logger = get_logger(__name__)


@click.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=8000, type=int, help='Port to bind to')
@click.option('--reload', is_flag=True, help='Enable auto-reload for development')
def api(host: str, port: int, reload: bool):
    """Run the API server with webhook endpoints.
    
    This starts the FastAPI server that handles:
    - Fireflies webhooks at /api/webhooks/fireflies
    - Health checks at /health
    - API documentation at /docs
    """
    try:
        logger.info(f"Starting API server on {host}:{port}")
        
        if reload:
            # For development with auto-reload
            import uvicorn
            uvicorn.run(
                "vector_db_query.api.app:app",
                host=host,
                port=port,
                reload=True
            )
        else:
            # For production
            run_api_server(host=host, port=port)
            
    except KeyboardInterrupt:
        logger.info("API server stopped by user")
    except Exception as e:
        logger.error(f"API server error: {e}")
        raise click.ClickException(str(e))


# Command aliases
run = api