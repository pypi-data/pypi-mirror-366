"""Server lifecycle management for MCP server."""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from ..vector_db.service import VectorDBService
from ..document_processor import DocumentProcessor
from .config import MCPSettings
from .server_enhanced import EnhancedVectorQueryMCPServer


logger = logging.getLogger(__name__)


class MCPServerManager:
    """Manages MCP server lifecycle."""
    
    def __init__(
        self,
        vector_service: Optional[VectorDBService] = None,
        document_processor: Optional[DocumentProcessor] = None,
        settings: Optional[MCPSettings] = None
    ):
        """Initialize server manager.
        
        Args:
            vector_service: Vector database service
            document_processor: Document processor for format support
            settings: MCP settings
        """
        self.vector_service = vector_service
        self.document_processor = document_processor or DocumentProcessor()
        self.settings = settings or MCPSettings.load_from_file()
        self.server: Optional[EnhancedVectorQueryMCPServer] = None
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = logging.DEBUG if os.getenv("MCP_DEBUG") else logging.INFO
        
        # Configure root logger
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stderr),
            ]
        )
        
        # Add file handler for audit logging
        if self.settings.audit_enabled:
            audit_handler = logging.FileHandler("logs/mcp_audit.log")
            audit_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            )
            logging.getLogger("mcp_audit").addHandler(audit_handler)
    
    async def initialize(self):
        """Initialize the server manager."""
        logger.info("Initializing MCP server manager...")
        
        # Initialize vector service if not provided
        if self.vector_service is None:
            self.vector_service = VectorDBService()
            await asyncio.to_thread(self.vector_service.initialize)
        
        # Create enhanced server instance with format support
        self.server = EnhancedVectorQueryMCPServer(
            vector_service=self.vector_service,
            document_processor=self.document_processor,
            server_config=self.settings.to_server_config()
        )
        
        logger.info("MCP server manager initialized")
    
    async def start(self):
        """Start the MCP server."""
        if self.server is None:
            await self.initialize()
        
        logger.info("Starting MCP server...")
        
        try:
            # Start server
            await self.server.start()
            
        except Exception as e:
            logger.error(f"Failed to start MCP server: {str(e)}")
            raise
    
    async def stop(self):
        """Stop the MCP server."""
        if self.server is None:
            logger.warning("No server to stop")
            return
        
        logger.info("Stopping MCP server...")
        
        try:
            await self.server.stop()
            self.server = None
            
        except Exception as e:
            logger.error(f"Error stopping server: {str(e)}")
            raise
    
    async def restart(self):
        """Restart the MCP server."""
        logger.info("Restarting MCP server...")
        await self.stop()
        await asyncio.sleep(1)  # Brief pause
        await self.start()
    
    def get_status(self) -> dict:
        """Get server status."""
        if self.server is None:
            return {
                "status": "not_initialized",
                "message": "Server not initialized"
            }
        
        return {
            "status": "running" if self.server._running else "stopped",
            "config": {
                "host": self.settings.server_host,
                "port": self.settings.server_port,
                "auth_enabled": self.settings.auth_enabled,
                "max_connections": self.settings.max_connections
            }
        }
    
    @asynccontextmanager
    async def run_server(self):
        """Context manager for running the server."""
        try:
            await self.initialize()
            await self.start()
            yield self.server
        finally:
            await self.stop()


async def run_mcp_server(config_path: Optional[Path] = None):
    """Run MCP server with default configuration.
    
    Args:
        config_path: Optional path to configuration file
    """
    # Load settings
    settings = MCPSettings.load_from_file(config_path)
    
    # Create manager
    manager = MCPServerManager(settings=settings)
    
    # Run server
    async with manager.run_server():
        logger.info("MCP server is running. Press Ctrl+C to stop.")
        
        # Keep running until interrupted
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            logger.info("Server shutdown requested")


def main():
    """Main entry point for MCP server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Vector DB Query MCP Server")
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to configuration file"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Set debug mode
    if args.debug:
        os.environ["MCP_DEBUG"] = "1"
    
    # Run server
    try:
        asyncio.run(run_mcp_server(args.config))
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()