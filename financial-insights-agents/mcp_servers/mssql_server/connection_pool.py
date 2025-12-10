"""Database connection pool management for MSSQL."""

import logging
import threading
from functools import lru_cache
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import QueuePool

logger = logging.getLogger(__name__)


class DatabaseConnectionPool:
    """Manages database connections with connection pooling."""

    def __init__(
        self,
        connection_string: str,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
    ) -> None:
        """Initialize database connection pool.

        Args:
            connection_string: SQLAlchemy connection string
            pool_size: Number of permanent connections in the pool
            max_overflow: Maximum overflow connections
            pool_timeout: Timeout in seconds for getting a connection
            pool_recycle: Recycle connections after this many seconds
        """
        self.connection_string = connection_string
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self._engine: Engine | None = None
        self._lock = threading.Lock()

        logger.info(
            f"Initializing database connection pool "
            f"(size={pool_size}, max_overflow={max_overflow})"
        )

    @property
    def engine(self) -> Engine:
        """Get or create the database engine.

        Returns:
            SQLAlchemy Engine instance
        """
        if self._engine is None:
            with self._lock:
                if self._engine is None:
                    self._engine = self._create_engine()
        return self._engine

    def _create_engine(self) -> Engine:
        """Create a new SQLAlchemy engine with connection pooling.

        Returns:
            SQLAlchemy Engine instance
        """
        logger.info("Creating new database engine")

        engine = create_engine(
            self.connection_string,
            poolclass=QueuePool,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            pool_timeout=self.pool_timeout,
            pool_recycle=self.pool_recycle,
            pool_pre_ping=True,  # Verify connections before using
            echo=False,  # Set to True for SQL debugging
        )

        # Test the connection
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection pool created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to create database connection pool: {e}")
            raise

        return engine

    def execute_query(
        self, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Execute a SQL query and return results.

        Args:
            query: SQL query to execute
            params: Optional query parameters

        Returns:
            List of result rows as dictionaries

        Raises:
            SQLAlchemyError: If query execution fails
        """
        logger.debug(f"Executing query: {query[:100]}...")

        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})

                if result.returns_rows:
                    rows = []
                    for row in result:
                        rows.append(dict(row._mapping))
                    logger.info(f"Query returned {len(rows)} rows")
                    return rows
                else:
                    logger.info("Query executed successfully (no rows returned)")
                    return []

        except SQLAlchemyError as e:
            logger.error(f"Query execution failed: {e}")
            raise

    def execute_many(
        self, query: str, params_list: list[dict[str, Any]]
    ) -> int:
        """Execute a SQL query multiple times with different parameters.

        Args:
            query: SQL query to execute
            params_list: List of parameter dictionaries

        Returns:
            Number of rows affected

        Raises:
            SQLAlchemyError: If query execution fails
        """
        logger.debug(f"Executing batch query with {len(params_list)} parameter sets")

        try:
            with self.engine.connect() as conn:
                with conn.begin():
                    for params in params_list:
                        conn.execute(text(query), params)
                logger.info(f"Batch query executed successfully")
                return len(params_list)

        except SQLAlchemyError as e:
            logger.error(f"Batch query execution failed: {e}")
            raise

    def get_table_names(self) -> list[str]:
        """Get list of all table names in the database.

        Returns:
            List of table names
        """
        query = """
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        AND TABLE_SCHEMA = 'dbo'
        ORDER BY TABLE_NAME;
        """

        results = self.execute_query(query)
        return [row["TABLE_NAME"] for row in results]

    def get_table_schema(self, table_name: str) -> list[dict[str, Any]]:
        """Get schema information for a specific table.

        Args:
            table_name: Name of the table

        Returns:
            List of column information dictionaries
        """
        query = """
        SELECT
            COLUMN_NAME,
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH,
            IS_NULLABLE,
            COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = :table_name
        AND TABLE_SCHEMA = 'dbo'
        ORDER BY ORDINAL_POSITION;
        """

        return self.execute_query(query, {"table_name": table_name})

    def get_table_sample(self, table_name: str, limit: int = 5) -> list[dict[str, Any]]:
        """Get sample rows from a table.

        Args:
            table_name: Name of the table
            limit: Number of rows to return

        Returns:
            List of sample rows
        """
        query = f"SELECT TOP {limit} * FROM dbo.{table_name};"
        return self.execute_query(query)

    def test_connection(self) -> bool:
        """Test if the database connection is working.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def get_pool_status(self) -> dict[str, Any]:
        """Get current connection pool status.

        Returns:
            Dictionary with pool status information
        """
        pool = self.engine.pool
        return {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total_connections": pool.size() + pool.overflow(),
        }

    def close(self) -> None:
        """Close all connections in the pool."""
        if self._engine is not None:
            logger.info("Closing database connection pool")
            self._engine.dispose()
            self._engine = None


@lru_cache(maxsize=1)
def get_connection_pool(connection_string: str) -> DatabaseConnectionPool:
    """Get or create a singleton connection pool.

    Args:
        connection_string: SQLAlchemy connection string

    Returns:
        DatabaseConnectionPool instance
    """
    return DatabaseConnectionPool(connection_string)
