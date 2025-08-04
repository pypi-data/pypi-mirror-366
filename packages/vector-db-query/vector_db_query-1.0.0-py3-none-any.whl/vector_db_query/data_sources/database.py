"""Database connection and session management for data sources."""

import os
from contextlib import asynccontextmanager, contextmanager
from typing import Optional, AsyncGenerator, Generator
import asyncpg
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

from .db_models import Base
from ..utils.logger import get_logger
from ..utils.config import get_config

logger = get_logger(__name__)


class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize database manager.
        
        Args:
            database_url: Database connection URL
        """
        self.database_url = database_url or self._get_database_url()
        self._engine = None
        self._async_engine = None
        self._sessionmaker = None
        self._async_sessionmaker = None
    
    def _get_database_url(self) -> str:
        """Get database URL from config or environment."""
        # Check environment variable first
        if os.environ.get('DATABASE_URL'):
            return os.environ['DATABASE_URL']
        
        # Build from config
        config = get_config()
        db_config = config.database if hasattr(config, 'database') else {}
        
        host = db_config.get('host', 'localhost')
        port = db_config.get('port', 5432)
        user = db_config.get('user', 'postgres')
        password = db_config.get('password', '')
        database = db_config.get('name', 'vector_db')
        
        if password:
            return f"postgresql://{user}:{password}@{host}:{port}/{database}"
        else:
            return f"postgresql://{user}@{host}:{port}/{database}"
    
    @property
    def engine(self):
        """Get or create synchronous SQLAlchemy engine."""
        if self._engine is None:
            self._engine = create_engine(
                self.database_url,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                echo=False  # Set to True for SQL debugging
            )
            logger.info("Created synchronous database engine")
        return self._engine
    
    @property
    def async_engine(self):
        """Get or create asynchronous SQLAlchemy engine."""
        if self._async_engine is None:
            # Convert to async URL format
            async_url = self.database_url.replace('postgresql://', 'postgresql+asyncpg://')
            
            self._async_engine = create_async_engine(
                async_url,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                echo=False  # Set to True for SQL debugging
            )
            logger.info("Created asynchronous database engine")
        return self._async_engine
    
    @property
    def session_factory(self) -> sessionmaker:
        """Get synchronous session factory."""
        if self._sessionmaker is None:
            self._sessionmaker = sessionmaker(
                bind=self.engine,
                expire_on_commit=False
            )
        return self._sessionmaker
    
    @property
    def async_session_factory(self) -> async_sessionmaker:
        """Get asynchronous session factory."""
        if self._async_sessionmaker is None:
            self._async_sessionmaker = async_sessionmaker(
                bind=self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
        return self._async_sessionmaker
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a synchronous database session.
        
        Yields:
            SQLAlchemy session
        """
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an asynchronous database session.
        
        Yields:
            Async SQLAlchemy session
        """
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def create_tables(self):
        """Create all tables asynchronously."""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Created all data source tables")
    
    def create_tables_sync(self):
        """Create all tables synchronously."""
        Base.metadata.create_all(self.engine)
        logger.info("Created all data source tables")
    
    async def drop_tables(self):
        """Drop all tables asynchronously (use with caution!)."""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.warning("Dropped all data source tables")
    
    async def test_connection(self) -> bool:
        """Test database connection.
        
        Returns:
            True if connection successful
        """
        try:
            async with self.get_async_session() as session:
                result = await session.execute("SELECT 1")
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def test_connection_sync(self) -> bool:
        """Test database connection synchronously.
        
        Returns:
            True if connection successful
        """
        try:
            with self.get_session() as session:
                result = session.execute("SELECT 1")
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    async def get_pool_status(self) -> dict:
        """Get connection pool status.
        
        Returns:
            Dict with pool statistics
        """
        pool = self.async_engine.pool
        return {
            'size': pool.size() if hasattr(pool, 'size') else 'N/A',
            'checked_in': pool.checkedin() if hasattr(pool, 'checkedin') else 'N/A',
            'checked_out': pool.checkedout() if hasattr(pool, 'checkedout') else 'N/A',
            'overflow': pool.overflow() if hasattr(pool, 'overflow') else 'N/A',
            'total': pool.total() if hasattr(pool, 'total') else 'N/A'
        }
    
    def close(self):
        """Close all database connections."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            logger.info("Closed synchronous database engine")
        
        if self._async_engine:
            # Note: async engine disposal should be done in async context
            logger.warning("Async engine should be closed in async context")
    
    async def aclose(self):
        """Close all database connections asynchronously."""
        if self._async_engine:
            await self._async_engine.dispose()
            self._async_engine = None
            logger.info("Closed asynchronous database engine")
        
        if self._engine:
            self._engine.dispose()
            self._engine = None
            logger.info("Closed synchronous database engine")


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance.
    
    Returns:
        DatabaseManager instance
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


# Convenience functions
def get_session() -> Generator[Session, None, None]:
    """Get a database session.
    
    Yields:
        SQLAlchemy session
    """
    db = get_db_manager()
    with db.get_session() as session:
        yield session


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session.
    
    Yields:
        Async SQLAlchemy session
    """
    db = get_db_manager()
    async with db.get_async_session() as session:
        yield session