"""
Database Data Loader - PostgreSQL implementation with versioning and optimization

This module provides PostgreSQL-specific data loading capabilities including:
- Connection pooling and transaction management
- Incremental loading with conflict resolution
- Data versioning and change tracking
- Bulk operations for performance
- Database optimization and statistics

Author: investByYourself Development Team
Created: August 2025
Phase: Tech-009 Phase 3 - Data Loading & Storage
"""

import asyncio
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import asyncpg
import structlog
from asyncpg.pool import Pool

from .base_loader import (BaseDataLoader, DataVersion, LoadingError,
                          LoadingMetrics, LoadingResult, LoadingStrategy,
                          StorageError, ValidationError)

# Configure structured logging
logger = structlog.get_logger(__name__)


@dataclass
class DatabaseConfig:
    """Configuration for database connection."""

    host: str = "localhost"
    port: int = 5432
    database: str = "investbyyourself"
    user: str = "etl_user"
    password: str = ""

    # Connection pool settings
    min_connections: int = 2
    max_connections: int = 10

    # Connection settings
    command_timeout: int = 60
    server_settings: Dict[str, str] = field(
        default_factory=lambda: {
            "application_name": "investbyyourself_etl",
            "timezone": "UTC",
        }
    )

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Create configuration from environment variables."""
        return cls(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_DATABASE", "investbyyourself"),
            user=os.getenv("DB_USER", "etl_user"),
            password=os.getenv("DB_PASSWORD", ""),
            min_connections=int(os.getenv("DB_MIN_CONNECTIONS", "2")),
            max_connections=int(os.getenv("DB_MAX_CONNECTIONS", "10")),
        )


class ConnectionPool:
    """Database connection pool manager."""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.pool: Optional[Pool] = None
        self.logger = logger.bind(component="connection_pool")

    async def initialize(self) -> None:
        """Initialize the connection pool."""
        try:
            self.pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.user,
                password=self.config.password,
                min_size=self.config.min_connections,
                max_size=self.config.max_connections,
                command_timeout=self.config.command_timeout,
                server_settings=self.config.server_settings,
            )
            self.logger.info("Database connection pool initialized")
        except Exception as e:
            self.logger.error("Failed to initialize connection pool", error=str(e))
            raise StorageError(f"Failed to initialize connection pool: {e}")

    async def close(self) -> None:
        """Close the connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
            self.logger.info("Database connection pool closed")

    def acquire(self):
        """Acquire a connection from the pool."""
        if not self.pool:
            raise StorageError("Connection pool not initialized")
        return self.pool.acquire()


class TransactionManager:
    """Transaction management for database operations."""

    def __init__(self, connection):
        self.connection = connection
        self.transaction = None
        self.logger = logger.bind(component="transaction_manager")

    async def begin(self) -> None:
        """Begin a new transaction."""
        if self.transaction:
            raise StorageError("Transaction already active")

        self.transaction = self.connection.transaction()
        await self.transaction.start()
        self.logger.debug("Transaction started")

    async def commit(self) -> None:
        """Commit the current transaction."""
        if not self.transaction:
            raise StorageError("No active transaction")

        await self.transaction.commit()
        self.transaction = None
        self.logger.debug("Transaction committed")

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        if not self.transaction:
            raise StorageError("No active transaction")

        await self.transaction.rollback()
        self.transaction = None
        self.logger.debug("Transaction rolled back")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.begin()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if exc_type:
            await self.rollback()
        else:
            await self.commit()


class DatabaseLoader(BaseDataLoader):
    """
    PostgreSQL database loader with versioning and optimization capabilities.

    Features:
    - Connection pooling for performance
    - Incremental loading strategies
    - Data versioning and change tracking
    - Bulk operations with COPY
    - Transaction management
    - Database optimization
    """

    def __init__(self, config: Optional[DatabaseConfig] = None, **kwargs):
        """
        Initialize the database loader.

        Args:
            config: Database configuration
            **kwargs: Additional base loader parameters
        """
        super().__init__(loader_id="database_loader", **kwargs)

        self.config = config or DatabaseConfig.from_env()
        self.pool = ConnectionPool(self.config)
        self.connection = None
        self.transaction_manager = None

        self.logger = logger.bind(loader_id=self.loader_id)

    async def connect(self) -> None:
        """Establish connection to the database."""
        try:
            await self.pool.initialize()
            self.is_connected = True
            self.logger.info("Database loader connected")
        except Exception as e:
            self.logger.error("Failed to connect to database", error=str(e))
            raise StorageError(f"Failed to connect to database: {e}")

    async def disconnect(self) -> None:
        """Close database connections."""
        try:
            if self.connection:
                await self.connection.close()
                self.connection = None

            await self.pool.close()
            self.is_connected = False
            self.logger.info("Database loader disconnected")
        except Exception as e:
            self.logger.error("Error during disconnect", error=str(e))

    async def load_data(
        self,
        data: Union[List[Dict[str, Any]], Dict[str, Any]],
        strategy: LoadingStrategy = LoadingStrategy.UPSERT,
        target_table: Optional[str] = None,
        **kwargs,
    ) -> LoadingResult:
        """
        Load data into the database using the specified strategy.

        Args:
            data: Data to load
            strategy: Loading strategy to use
            target_table: Target table name
            **kwargs: Additional parameters

        Returns:
            LoadingResult with metrics and status
        """
        if not self.is_connected:
            raise StorageError("Database loader not connected")

        # Normalize data to list
        if isinstance(data, dict):
            data = [data]

        if not data:
            return LoadingResult(
                success=True, metrics=LoadingMetrics(start_time=datetime.now())
            )

        # Initialize metrics
        self.metrics = LoadingMetrics(start_time=datetime.now())
        result = LoadingResult(success=True, metrics=self.metrics)

        try:
            # Process data in batches
            async with self.pool.acquire() as connection:
                self.connection = connection
                self.transaction_manager = TransactionManager(connection)

                # Create data version if versioning enabled
                data_version = None
                if self.enable_versioning and target_table:
                    checksum = self.calculate_checksum(data)
                    data_version = await self.create_data_version(
                        target_table, len(data), checksum, kwargs.get("metadata", {})
                    )
                    result.data_version = data_version

                # Process batches
                for i in range(0, len(data), self.batch_size):
                    batch = data[i : i + self.batch_size]
                    batch_result = await self.process_batch(
                        batch, strategy, target_table, **kwargs
                    )

                    # Aggregate metrics
                    self._aggregate_metrics(batch_result.metrics)

                    if not batch_result.success:
                        result.success = False
                        result.errors.extend(batch_result.errors)

                # Optimize storage if successful
                if result.success and target_table:
                    await self._optimize_table(target_table)

        except Exception as e:
            self.logger.error("Error during data loading", error=str(e))
            result.success = False
            result.add_error(f"Data loading failed: {str(e)}")

        finally:
            # Finalize metrics
            self.metrics.end_time = datetime.now()
            self.metrics.duration_seconds = (
                self.metrics.end_time - self.metrics.start_time
            ).total_seconds()

            result.metrics = self.metrics
            self.connection = None
            self.transaction_manager = None

        return result

    async def _load_batch(
        self,
        batch: List[Dict[str, Any]],
        strategy: LoadingStrategy,
        target_table: str,
        **kwargs,
    ) -> LoadingResult:
        """Load a batch of records using the specified strategy."""
        result = LoadingResult(
            success=True, metrics=LoadingMetrics(start_time=datetime.now())
        )

        try:
            async with self.transaction_manager:
                if strategy == LoadingStrategy.INSERT_ONLY:
                    await self._insert_batch(batch, target_table, result)
                elif strategy == LoadingStrategy.UPDATE_ONLY:
                    await self._update_batch(batch, target_table, result)
                elif strategy == LoadingStrategy.UPSERT:
                    await self._upsert_batch(batch, target_table, result)
                elif strategy == LoadingStrategy.REPLACE:
                    await self._replace_batch(batch, target_table, result)
                elif strategy == LoadingStrategy.APPEND:
                    await self._insert_batch(
                        batch, target_table, result
                    )  # Same as insert
                else:
                    raise ValueError(f"Unsupported loading strategy: {strategy}")

        except Exception as e:
            result.success = False
            result.add_error(f"Batch loading failed: {str(e)}")

        return result

    async def _insert_batch(
        self, batch: List[Dict[str, Any]], target_table: str, result: LoadingResult
    ) -> None:
        """Insert batch using bulk COPY operation."""
        if not batch:
            return

        try:
            # Prepare data for COPY
            columns = list(batch[0].keys())
            values = [tuple(record.get(col) for col in columns) for record in batch]

            # Use COPY for bulk insert
            await self.connection.copy_records_to_table(
                target_table, records=values, columns=columns
            )

            result.metrics.records_inserted += len(batch)
            result.metrics.records_processed += len(batch)

        except Exception as e:
            self.logger.error("Insert batch failed", error=str(e))
            raise

    async def _update_batch(
        self, batch: List[Dict[str, Any]], target_table: str, result: LoadingResult
    ) -> None:
        """Update batch using individual UPDATE statements."""
        for record in batch:
            try:
                # Assuming 'id' or first column is the primary key
                pk_column = list(record.keys())[0]
                pk_value = record[pk_column]

                # Build UPDATE statement
                set_clause = ", ".join(
                    [
                        f"{col} = ${i+2}"
                        for i, col in enumerate(record.keys())
                        if col != pk_column
                    ]
                )
                values = [pk_value] + [v for k, v in record.items() if k != pk_column]

                query = f"UPDATE {target_table} SET {set_clause} WHERE {pk_column} = $1"

                rows_affected = await self.connection.execute(query, *values)

                if rows_affected > 0:
                    result.metrics.records_updated += 1
                else:
                    result.metrics.records_skipped += 1

                result.metrics.records_processed += 1

            except Exception as e:
                result.metrics.records_failed += 1
                result.add_warning(f"Failed to update record {record}: {str(e)}")

    async def _upsert_batch(
        self, batch: List[Dict[str, Any]], target_table: str, result: LoadingResult
    ) -> None:
        """Upsert batch using ON CONFLICT clause."""
        if not batch:
            return

        try:
            # Get table info to determine conflict column
            table_info = await self._get_table_info(target_table)
            primary_key = table_info.get("primary_key", "id")

            columns = list(batch[0].keys())
            placeholders = ", ".join([f"${i+1}" for i in range(len(columns))])

            # Build conflict resolution clause
            update_clause = ", ".join(
                [f"{col} = EXCLUDED.{col}" for col in columns if col != primary_key]
            )

            query = f"""
                INSERT INTO {target_table} ({', '.join(columns)})
                VALUES ({placeholders})
                ON CONFLICT ({primary_key}) DO UPDATE SET {update_clause}
                RETURNING (xmax = 0) AS inserted
            """

            for record in batch:
                values = [record[col] for col in columns]
                row = await self.connection.fetchrow(query, *values)

                if row["inserted"]:
                    result.metrics.records_inserted += 1
                else:
                    result.metrics.records_updated += 1

                result.metrics.records_processed += 1

        except Exception as e:
            self.logger.error("Upsert batch failed", error=str(e))
            raise

    async def _replace_batch(
        self, batch: List[Dict[str, Any]], target_table: str, result: LoadingResult
    ) -> None:
        """Replace entire table with batch data."""
        try:
            # Truncate table first
            await self.connection.execute(f"TRUNCATE TABLE {target_table}")

            # Insert new data
            await self._insert_batch(batch, target_table, result)

        except Exception as e:
            self.logger.error("Replace batch failed", error=str(e))
            raise

    async def get_data_version(self, target: str) -> Optional[DataVersion]:
        """Get the current data version for a target table."""
        try:
            async with self.pool.acquire() as connection:
                query = """
                    SELECT version_id, timestamp, checksum, record_count,
                           schema_version, source, metadata
                    FROM data_versions
                    WHERE target_table = $1
                    ORDER BY timestamp DESC
                    LIMIT 1
                """
                row = await connection.fetchrow(query, target)

                if row:
                    return DataVersion(
                        version_id=row["version_id"],
                        timestamp=row["timestamp"],
                        checksum=row["checksum"],
                        record_count=row["record_count"],
                        schema_version=row["schema_version"],
                        source=row["source"],
                        metadata=row["metadata"] or {},
                    )

                return None

        except Exception as e:
            self.logger.error("Failed to get data version", error=str(e))
            return None

    async def create_data_version(
        self,
        target: str,
        record_count: int,
        checksum: str,
        metadata: Dict[str, Any] = None,
    ) -> DataVersion:
        """Create a new data version entry."""
        import uuid

        version = DataVersion(
            version_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            checksum=checksum,
            record_count=record_count,
            schema_version="1.0",
            source=self.loader_id,
            metadata=metadata or {},
        )

        try:
            async with self.pool.acquire() as connection:
                query = """
                    INSERT INTO data_versions
                    (version_id, target_table, timestamp, checksum, record_count,
                     schema_version, source, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """
                await connection.execute(
                    query,
                    version.version_id,
                    target,
                    version.timestamp,
                    version.checksum,
                    version.record_count,
                    version.schema_version,
                    version.source,
                    version.metadata,
                )

                self.logger.info("Created data version", version_id=version.version_id)
                return version

        except Exception as e:
            self.logger.error("Failed to create data version", error=str(e))
            raise StorageError(f"Failed to create data version: {e}")

    async def _get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get table information including primary key."""
        try:
            query = """
                SELECT column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                WHERE tc.table_name = $1 AND tc.constraint_type = 'PRIMARY KEY'
                LIMIT 1
            """
            row = await self.connection.fetchrow(query, table_name)

            return {
                "primary_key": row["column_name"] if row else "id",
                "table_name": table_name,
            }

        except Exception as e:
            self.logger.warning("Failed to get table info", error=str(e))
            return {"primary_key": "id", "table_name": table_name}

    async def _optimize_table(self, table_name: str) -> None:
        """Optimize table performance."""
        try:
            # Analyze table statistics
            await self.connection.execute(f"ANALYZE {table_name}")
            self.logger.debug("Table analyzed", table=table_name)

        except Exception as e:
            self.logger.warning("Table optimization failed", error=str(e))

    async def optimize_storage(self, target: str) -> Dict[str, Any]:
        """Optimize storage for the target table."""
        try:
            async with self.pool.acquire() as connection:
                # Vacuum and analyze
                await connection.execute(f"VACUUM ANALYZE {target}")

                # Get table statistics
                stats_query = """
                    SELECT
                        schemaname, tablename, attname, n_distinct, correlation
                    FROM pg_stats
                    WHERE tablename = $1
                """
                stats = await connection.fetch(stats_query, target)

                return {
                    "status": "optimized",
                    "target": target,
                    "statistics": [dict(row) for row in stats],
                }

        except Exception as e:
            self.logger.error("Storage optimization failed", error=str(e))
            return {"status": "failed", "target": target, "error": str(e)}

    async def get_statistics(self, target: str) -> Dict[str, Any]:
        """Get comprehensive statistics for the target table."""
        try:
            async with self.pool.acquire() as connection:
                # Table size and row count
                size_query = """
                    SELECT
                        pg_size_pretty(pg_total_relation_size($1)) as total_size,
                        pg_size_pretty(pg_relation_size($1)) as table_size,
                        (SELECT reltuples::bigint FROM pg_class WHERE relname = $1) as estimated_rows
                """
                size_info = await connection.fetchrow(size_query, target)

                # Index information
                index_query = """
                    SELECT indexname, indexdef
                    FROM pg_indexes
                    WHERE tablename = $1
                """
                indexes = await connection.fetch(index_query, target)

                return {
                    "table": target,
                    "total_size": size_info["total_size"],
                    "table_size": size_info["table_size"],
                    "estimated_rows": size_info["estimated_rows"],
                    "indexes": [dict(idx) for idx in indexes],
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            self.logger.error("Failed to get statistics", error=str(e))
            return {"status": "failed", "target": target, "error": str(e)}

    def _aggregate_metrics(self, batch_metrics: LoadingMetrics) -> None:
        """Aggregate metrics from batch processing."""
        self.metrics.records_processed += batch_metrics.records_processed
        self.metrics.records_inserted += batch_metrics.records_inserted
        self.metrics.records_updated += batch_metrics.records_updated
        self.metrics.records_skipped += batch_metrics.records_skipped
        self.metrics.records_failed += batch_metrics.records_failed
        self.metrics.validation_errors += batch_metrics.validation_errors
