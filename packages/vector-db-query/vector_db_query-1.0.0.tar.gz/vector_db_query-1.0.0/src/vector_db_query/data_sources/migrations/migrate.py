"""Database migration runner for data sources."""

import asyncio
import asyncpg
from pathlib import Path
from typing import List, Optional
import os
import sys
from datetime import datetime

from ...utils.logger import get_logger
from ...utils.config import get_config

logger = get_logger(__name__)


class MigrationRunner:
    """Handles database migrations for data source tables."""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize migration runner.
        
        Args:
            database_url: PostgreSQL connection URL
        """
        self.database_url = database_url or self._get_database_url()
        self.migrations_dir = Path(__file__).parent
        
    def _get_database_url(self) -> str:
        """Get database URL from config or environment."""
        config = get_config()
        
        # Check environment variable first
        if os.environ.get('DATABASE_URL'):
            return os.environ['DATABASE_URL']
        
        # Build from config
        db_config = config.get('database', {})
        host = db_config.get('host', 'localhost')
        port = db_config.get('port', 5432)
        user = db_config.get('user', 'postgres')
        password = db_config.get('password', '')
        database = db_config.get('name', 'vector_db')
        
        if password:
            return f"postgresql://{user}:{password}@{host}:{port}/{database}"
        else:
            return f"postgresql://{user}@{host}:{port}/{database}"
    
    async def create_migrations_table(self, conn: asyncpg.Connection):
        """Create migrations tracking table if not exists."""
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(50) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("Migrations table ready")
    
    async def get_applied_migrations(self, conn: asyncpg.Connection) -> List[str]:
        """Get list of applied migration versions."""
        rows = await conn.fetch(
            "SELECT version FROM schema_migrations ORDER BY version"
        )
        return [row['version'] for row in rows]
    
    async def apply_migration(self, conn: asyncpg.Connection, migration_file: Path):
        """Apply a single migration file."""
        version = migration_file.stem.split('_')[0]  # Extract version number
        name = migration_file.stem
        
        # Read migration content
        sql_content = migration_file.read_text()
        
        try:
            # Begin transaction
            async with conn.transaction():
                # Execute migration
                await conn.execute(sql_content)
                
                # Record migration
                await conn.execute(
                    "INSERT INTO schema_migrations (version, name) VALUES ($1, $2)",
                    version, name
                )
                
            logger.info(f"Applied migration: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply migration {name}: {e}")
            return False
    
    async def run_migrations(self):
        """Run all pending migrations."""
        logger.info("Starting database migrations...")
        
        # Connect to database
        conn = await asyncpg.connect(self.database_url)
        
        try:
            # Create migrations table
            await self.create_migrations_table(conn)
            
            # Get applied migrations
            applied = await self.get_applied_migrations(conn)
            logger.info(f"Found {len(applied)} applied migrations")
            
            # Find migration files
            migration_files = sorted(
                self.migrations_dir.glob("*.sql"),
                key=lambda f: f.name
            )
            
            # Apply pending migrations
            pending_count = 0
            for migration_file in migration_files:
                version = migration_file.stem.split('_')[0]
                
                if version not in applied:
                    logger.info(f"Applying migration: {migration_file.name}")
                    success = await self.apply_migration(conn, migration_file)
                    
                    if not success:
                        logger.error("Migration failed, stopping")
                        return False
                    
                    pending_count += 1
            
            if pending_count == 0:
                logger.info("No pending migrations")
            else:
                logger.info(f"Applied {pending_count} migrations successfully")
            
            return True
            
        finally:
            await conn.close()
    
    async def rollback_migration(self, version: str):
        """Rollback a specific migration (if rollback script exists)."""
        # Note: Rollback functionality would require down migrations
        logger.warning("Rollback not implemented - manual intervention required")
        return False
    
    async def get_migration_status(self) -> dict:
        """Get current migration status."""
        conn = await asyncpg.connect(self.database_url)
        
        try:
            # Ensure migrations table exists
            await self.create_migrations_table(conn)
            
            # Get applied migrations
            applied = await self.get_applied_migrations(conn)
            
            # Find all migration files
            all_migrations = sorted(
                [f.stem for f in self.migrations_dir.glob("*.sql")]
            )
            
            # Find pending migrations
            pending = [
                m for m in all_migrations 
                if m.split('_')[0] not in applied
            ]
            
            return {
                'applied': applied,
                'pending': pending,
                'total': len(all_migrations),
                'up_to_date': len(pending) == 0
            }
            
        finally:
            await conn.close()


async def main():
    """CLI entry point for migration runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Data source database migrations')
    parser.add_argument('command', choices=['migrate', 'status', 'rollback'],
                       help='Migration command to run')
    parser.add_argument('--version', help='Migration version (for rollback)')
    parser.add_argument('--database-url', help='Database connection URL')
    
    args = parser.parse_args()
    
    # Create runner
    runner = MigrationRunner(database_url=args.database_url)
    
    if args.command == 'migrate':
        success = await runner.run_migrations()
        sys.exit(0 if success else 1)
        
    elif args.command == 'status':
        status = await runner.get_migration_status()
        print(f"\nMigration Status:")
        print(f"  Applied: {len(status['applied'])}")
        print(f"  Pending: {len(status['pending'])}")
        print(f"  Total: {status['total']}")
        print(f"  Up to date: {'Yes' if status['up_to_date'] else 'No'}")
        
        if status['pending']:
            print(f"\nPending migrations:")
            for m in status['pending']:
                print(f"  - {m}")
                
    elif args.command == 'rollback':
        if not args.version:
            print("Error: --version required for rollback")
            sys.exit(1)
        
        success = await runner.rollback_migration(args.version)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    asyncio.run(main())