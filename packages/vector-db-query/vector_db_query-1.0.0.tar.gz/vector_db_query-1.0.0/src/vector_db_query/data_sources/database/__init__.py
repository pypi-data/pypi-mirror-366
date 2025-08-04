"""Database components for data sources."""

from .manager import DataSourceDatabaseManager

# Global database manager instance
_db_manager = None


def get_db_manager(connection_string: str = None) -> DataSourceDatabaseManager:
    """Get or create database manager instance.
    
    Args:
        connection_string: Database connection string (optional)
        
    Returns:
        Database manager instance
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DataSourceDatabaseManager(connection_string)
    return _db_manager


__all__ = ['DataSourceDatabaseManager', 'get_db_manager']