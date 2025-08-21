"""
Cache Data Loader - Redis-based caching with TTL and performance optimization

This module provides Redis cache loading capabilities including:
- High-performance data caching
- TTL (Time To Live) management
- Cache invalidation strategies
- Performance metrics and monitoring
- Key namespace organization

Author: investByYourself Development Team
Created: August 2025
Phase: Tech-009 Phase 3 - Data Loading & Storage
"""

import asyncio
import json
import pickle
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import structlog

from .base_loader import (
    BaseDataLoader,
    DataVersion,
    LoadingError,
    LoadingMetrics,
    LoadingResult,
    LoadingStrategy,
    StorageError,
    ValidationError,
)

# Configure structured logging
logger = structlog.get_logger(__name__)


class SerializationFormat(Enum):
    """Serialization formats for cache data."""

    JSON = "json"
    PICKLE = "pickle"
    STRING = "string"


@dataclass
class CacheConfig:
    """Configuration for Redis cache connection."""

    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = "secure_redis_2025"
    database: int = 0

    # Connection pool settings
    max_connections: int = 20
    retry_on_timeout: bool = True
    health_check_interval: int = 30

    # Default cache settings
    default_ttl: int = 3600  # 1 hour
    key_prefix: str = "investbyyourself"

    @classmethod
    def from_env(cls) -> "CacheConfig":
        """Create configuration from environment variables."""
        import os

        return cls(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD", "secure_redis_2025"),
            database=int(os.getenv("REDIS_DATABASE", "0")),
            max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "20")),
            default_ttl=int(os.getenv("REDIS_DEFAULT_TTL", "3600")),
            key_prefix=os.getenv("REDIS_KEY_PREFIX", "investbyyourself"),
        )


@dataclass
class CacheMetrics:
    """Metrics for cache operations."""

    # Hit/Miss statistics
    cache_hits: int = 0
    cache_misses: int = 0
    cache_sets: int = 0
    cache_deletes: int = 0
    cache_expires: int = 0

    # Performance metrics
    avg_get_time_ms: float = 0.0
    avg_set_time_ms: float = 0.0
    total_operations: int = 0

    # Memory usage
    memory_usage_bytes: int = 0
    key_count: int = 0

    def hit_ratio(self) -> float:
        """Calculate cache hit ratio."""
        total_gets = self.cache_hits + self.cache_misses
        if total_gets > 0:
            return self.cache_hits / total_gets
        return 0.0


class TTLManager:
    """Manages TTL (Time To Live) for cache keys."""

    def __init__(self, default_ttl: int = 3600):
        self.default_ttl = default_ttl
        self.ttl_policies: Dict[str, int] = {}

    def set_policy(self, pattern: str, ttl_seconds: int) -> None:
        """Set TTL policy for key patterns."""
        self.ttl_policies[pattern] = ttl_seconds

    def get_ttl(self, key: str) -> int:
        """Get TTL for a specific key based on policies."""
        # Check for pattern matches
        for pattern, ttl in self.ttl_policies.items():
            if pattern in key:
                return ttl

        return self.default_ttl


class CacheLoader(BaseDataLoader):
    """
    Redis-based cache loader with TTL management and performance optimization.

    Features:
    - High-performance data caching
    - TTL management with policies
    - Multiple serialization formats
    - Cache invalidation strategies
    - Performance monitoring
    - Key namespace organization
    """

    def __init__(
        self,
        config: Optional[CacheConfig] = None,
        serialization_format: SerializationFormat = SerializationFormat.JSON,
        **kwargs,
    ):
        """
        Initialize the cache loader.

        Args:
            config: Redis configuration
            serialization_format: Default serialization format
            **kwargs: Additional base loader parameters
        """
        super().__init__(loader_id="cache_loader", **kwargs)

        self.config = config or CacheConfig.from_env()
        self.serialization_format = serialization_format
        self.ttl_manager = TTLManager(self.config.default_ttl)

        # Redis connection
        self.redis_client = None
        self.connection_pool = None

        # Metrics
        self.cache_metrics = CacheMetrics()

        self.logger = logger.bind(loader_id=self.loader_id)

    async def connect(self) -> None:
        """Establish connection to Redis."""
        try:
            import redis.asyncio as redis

            # Create connection pool
            self.connection_pool = redis.ConnectionPool(
                host=self.config.host,
                port=self.config.port,
                password=self.config.password,
                db=self.config.database,
                max_connections=self.config.max_connections,
                retry_on_timeout=self.config.retry_on_timeout,
                health_check_interval=self.config.health_check_interval,
            )

            # Create Redis client
            self.redis_client = redis.Redis(connection_pool=self.connection_pool)

            # Test connection
            await self.redis_client.ping()

            self.is_connected = True
            self.logger.info("Cache loader connected to Redis")

        except ImportError:
            raise StorageError(
                "redis package not installed. Install with: pip install redis"
            )
        except Exception as e:
            self.logger.error("Failed to connect to Redis", error=str(e))
            raise StorageError(f"Failed to connect to Redis: {e}")

    async def disconnect(self) -> None:
        """Close Redis connections."""
        try:
            if self.redis_client:
                await self.redis_client.close()
                self.redis_client = None

            if self.connection_pool:
                await self.connection_pool.disconnect()
                self.connection_pool = None

            self.is_connected = False
            self.logger.info("Cache loader disconnected")

        except Exception as e:
            self.logger.error("Error during disconnect", error=str(e))

    async def load_data(
        self,
        data: Union[List[Dict[str, Any]], Dict[str, Any]],
        strategy: LoadingStrategy = LoadingStrategy.UPSERT,
        target_table: Optional[str] = None,
        ttl: Optional[int] = None,
        key_pattern: Optional[str] = None,
        **kwargs,
    ) -> LoadingResult:
        """
        Load data into cache using the specified strategy.

        Args:
            data: Data to cache
            strategy: Loading strategy to use
            target_table: Cache key prefix/namespace
            ttl: Time to live in seconds
            key_pattern: Key pattern for generating cache keys
            **kwargs: Additional parameters

        Returns:
            LoadingResult with metrics and status
        """
        if not self.is_connected:
            raise StorageError("Cache loader not connected")

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
            # Process data based on strategy
            if strategy == LoadingStrategy.REPLACE:
                # Clear existing keys first
                if target_table:
                    await self._clear_namespace(target_table)

            # Cache all records
            for record in data:
                cache_key = self._generate_cache_key(record, target_table, key_pattern)
                ttl_value = ttl or self.ttl_manager.get_ttl(cache_key)

                success = await self._set_cache(cache_key, record, ttl_value)

                if success:
                    self.metrics.records_inserted += 1
                else:
                    self.metrics.records_failed += 1

                self.metrics.records_processed += 1

            # Create data version if versioning enabled
            if self.enable_versioning and target_table:
                checksum = self.calculate_checksum(data)
                data_version = await self.create_data_version(
                    target_table, len(data), checksum, {"cache_namespace": target_table}
                )
                result.data_version = data_version

        except Exception as e:
            self.logger.error("Error during cache loading", error=str(e))
            result.success = False
            result.add_error(f"Cache loading failed: {str(e)}")

        finally:
            # Finalize metrics
            self.metrics.end_time = datetime.now()
            self.metrics.duration_seconds = (
                self.metrics.end_time - self.metrics.start_time
            ).total_seconds()

            result.metrics = self.metrics

        return result

    async def _load_batch(
        self,
        batch: List[Dict[str, Any]],
        strategy: LoadingStrategy,
        target_table: str,
        **kwargs,
    ) -> LoadingResult:
        """Load a batch of records to cache."""
        # For cache loading, we process records individually
        # but could optimize with Redis pipelines
        return LoadingResult(
            success=True, metrics=LoadingMetrics(start_time=datetime.now())
        )

    async def _set_cache(
        self,
        key: str,
        value: Any,
        ttl: int,
        format_override: Optional[SerializationFormat] = None,
    ) -> bool:
        """Set a value in cache with TTL."""
        try:
            start_time = datetime.now()

            # Serialize value
            serialized_value = self._serialize_value(value, format_override)

            # Set in Redis with TTL
            await self.redis_client.setex(key, ttl, serialized_value)

            # Update metrics
            end_time = datetime.now()
            operation_time = (end_time - start_time).total_seconds() * 1000
            self.cache_metrics.cache_sets += 1
            self.cache_metrics.avg_set_time_ms = (
                self.cache_metrics.avg_set_time_ms * (self.cache_metrics.cache_sets - 1)
                + operation_time
            ) / self.cache_metrics.cache_sets

            return True

        except Exception as e:
            self.logger.error("Failed to set cache", key=key, error=str(e))
            return False

    async def get_cache(
        self, key: str, format_override: Optional[SerializationFormat] = None
    ) -> Optional[Any]:
        """Get a value from cache."""
        try:
            start_time = datetime.now()

            # Get from Redis
            raw_value = await self.redis_client.get(key)

            # Update metrics
            end_time = datetime.now()
            operation_time = (end_time - start_time).total_seconds() * 1000

            if raw_value is not None:
                self.cache_metrics.cache_hits += 1
                # Deserialize value
                value = self._deserialize_value(raw_value, format_override)
            else:
                self.cache_metrics.cache_misses += 1
                value = None

            # Update average get time
            total_gets = self.cache_metrics.cache_hits + self.cache_metrics.cache_misses
            self.cache_metrics.avg_get_time_ms = (
                self.cache_metrics.avg_get_time_ms * (total_gets - 1) + operation_time
            ) / total_gets

            return value

        except Exception as e:
            self.logger.error("Failed to get cache", key=key, error=str(e))
            self.cache_metrics.cache_misses += 1
            return None

    async def delete_cache(self, key: str) -> bool:
        """Delete a key from cache."""
        try:
            result = await self.redis_client.delete(key)
            self.cache_metrics.cache_deletes += 1
            return result > 0

        except Exception as e:
            self.logger.error("Failed to delete cache", key=key, error=str(e))
            return False

    async def _clear_namespace(self, namespace: str) -> int:
        """Clear all keys in a namespace."""
        try:
            pattern = f"{self.config.key_prefix}:{namespace}:*"
            keys = await self.redis_client.keys(pattern)

            if keys:
                deleted = await self.redis_client.delete(*keys)
                self.cache_metrics.cache_deletes += deleted
                return deleted

            return 0

        except Exception as e:
            self.logger.error(
                "Failed to clear namespace", namespace=namespace, error=str(e)
            )
            return 0

    def _generate_cache_key(
        self,
        record: Dict[str, Any],
        namespace: Optional[str] = None,
        pattern: Optional[str] = None,
    ) -> str:
        """Generate cache key for a record."""

        # Build key components
        key_parts = [self.config.key_prefix]

        if namespace:
            key_parts.append(namespace)

        if pattern:
            # Replace placeholders in pattern with record values
            key_suffix = pattern
            for field, value in record.items():
                key_suffix = key_suffix.replace(f"{{{field}}}", str(value))
            key_parts.append(key_suffix)
        else:
            # Generate key from record ID or hash
            if "id" in record:
                key_parts.append(str(record["id"]))
            elif "symbol" in record:
                key_parts.append(str(record["symbol"]))
            else:
                # Use checksum as key
                key_parts.append(self.calculate_checksum(record)[:8])

        return ":".join(key_parts)

    def _serialize_value(
        self, value: Any, format_override: Optional[SerializationFormat] = None
    ) -> bytes:
        """Serialize value for storage in Redis."""

        format_to_use = format_override or self.serialization_format

        try:
            if format_to_use == SerializationFormat.JSON:
                return json.dumps(value, default=str).encode("utf-8")
            elif format_to_use == SerializationFormat.PICKLE:
                return pickle.dumps(value)
            elif format_to_use == SerializationFormat.STRING:
                return str(value).encode("utf-8")
            else:
                raise ValueError(f"Unsupported serialization format: {format_to_use}")

        except Exception as e:
            self.logger.error(
                "Serialization failed", format=format_to_use.value, error=str(e)
            )
            raise StorageError(f"Failed to serialize value: {e}")

    def _deserialize_value(
        self, raw_value: bytes, format_override: Optional[SerializationFormat] = None
    ) -> Any:
        """Deserialize value from Redis storage."""

        format_to_use = format_override or self.serialization_format

        try:
            if format_to_use == SerializationFormat.JSON:
                return json.loads(raw_value.decode("utf-8"))
            elif format_to_use == SerializationFormat.PICKLE:
                return pickle.loads(raw_value)
            elif format_to_use == SerializationFormat.STRING:
                return raw_value.decode("utf-8")
            else:
                raise ValueError(f"Unsupported serialization format: {format_to_use}")

        except Exception as e:
            self.logger.error(
                "Deserialization failed", format=format_to_use.value, error=str(e)
            )
            raise StorageError(f"Failed to deserialize value: {e}")

    async def get_data_version(self, target: str) -> Optional[DataVersion]:
        """Get the current data version for a cache namespace."""
        try:
            version_key = f"{self.config.key_prefix}:versions:{target}"
            version_data = await self.get_cache(version_key)

            if version_data:
                return DataVersion(
                    version_id=version_data["version_id"],
                    timestamp=datetime.fromisoformat(version_data["timestamp"]),
                    checksum=version_data["checksum"],
                    record_count=version_data["record_count"],
                    schema_version=version_data["schema_version"],
                    source=version_data["source"],
                    metadata=version_data.get("metadata", {}),
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
        """Create a new data version entry in cache."""
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
            version_key = f"{self.config.key_prefix}:versions:{target}"
            version_data = {
                "version_id": version.version_id,
                "timestamp": version.timestamp.isoformat(),
                "checksum": version.checksum,
                "record_count": version.record_count,
                "schema_version": version.schema_version,
                "source": version.source,
                "metadata": version.metadata,
            }

            # Store version with longer TTL (24 hours)
            await self._set_cache(version_key, version_data, 86400)

            self.logger.info(
                "Created data version", version_id=version.version_id, target=target
            )
            return version

        except Exception as e:
            self.logger.error("Failed to create data version", error=str(e))
            raise StorageError(f"Failed to create data version: {e}")

    async def optimize_storage(self, target: str) -> Dict[str, Any]:
        """Optimize cache storage (analyze memory usage and suggest optimizations)."""
        try:
            # Get Redis memory info
            memory_info = await self.redis_client.info("memory")

            # Get key count for namespace
            pattern = f"{self.config.key_prefix}:{target}:*"
            keys = await self.redis_client.keys(pattern)
            key_count = len(keys)

            # Sample key sizes (first 10 keys)
            sample_sizes = []
            for key in keys[:10]:
                try:
                    size = await self.redis_client.memory_usage(key)
                    if size:
                        sample_sizes.append(size)
                except:
                    pass

            avg_key_size = sum(sample_sizes) / len(sample_sizes) if sample_sizes else 0
            estimated_namespace_size = avg_key_size * key_count

            return {
                "status": "analyzed",
                "target": target,
                "key_count": key_count,
                "estimated_size_bytes": estimated_namespace_size,
                "avg_key_size_bytes": avg_key_size,
                "redis_memory_used": memory_info.get("used_memory", 0),
                "redis_memory_human": memory_info.get("used_memory_human", "unknown"),
                "cache_metrics": {
                    "hit_ratio": self.cache_metrics.hit_ratio(),
                    "total_operations": self.cache_metrics.cache_hits
                    + self.cache_metrics.cache_misses,
                    "avg_get_time_ms": self.cache_metrics.avg_get_time_ms,
                    "avg_set_time_ms": self.cache_metrics.avg_set_time_ms,
                },
            }

        except Exception as e:
            return {"status": "failed", "target": target, "error": str(e)}

    async def get_statistics(self, target: str) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        try:
            pattern = f"{self.config.key_prefix}:{target}:*"
            keys = await self.redis_client.keys(pattern)

            # Get TTL information for sample keys
            ttl_info = []
            for key in keys[:5]:  # Sample first 5 keys
                ttl = await self.redis_client.ttl(key)
                ttl_info.append(ttl)

            return {
                "namespace": target,
                "key_count": len(keys),
                "sample_ttls": ttl_info,
                "cache_metrics": {
                    "hits": self.cache_metrics.cache_hits,
                    "misses": self.cache_metrics.cache_misses,
                    "sets": self.cache_metrics.cache_sets,
                    "deletes": self.cache_metrics.cache_deletes,
                    "hit_ratio": self.cache_metrics.hit_ratio(),
                    "avg_get_time_ms": self.cache_metrics.avg_get_time_ms,
                    "avg_set_time_ms": self.cache_metrics.avg_set_time_ms,
                },
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"status": "failed", "target": target, "error": str(e)}
