"""
Data Loading Package - Phase 3 of TECH-009 ETL Pipeline Implementation

This package provides data loading capabilities for the investByYourself ETL pipeline,
including incremental loading, versioning, archiving, and export functionalities.

Components:
- BaseDataLoader: Abstract base class for all data loaders
- DatabaseLoader: PostgreSQL database loading with versioning
- FileLoader: File-based loading (CSV, JSON, Parquet)
- CacheLoader: Redis cache loading for fast access
- ArchiveLoader: Data archiving and retention management
- ExportLoader: Data export for analysis tools

Phase 3 Goals:
1. Incremental data loading strategies
2. Data versioning and change tracking
3. Data archiving and retention policies
4. Data compression and optimization
5. Data export capabilities for analysis tools
"""

from .base_loader import (BaseDataLoader, DataVersion, LoadingError,
                          LoadingMetrics, LoadingResult, LoadingStrategy,
                          StorageError, ValidationError)
# File loader (no external dependencies required)
from .file_loader import CompressionType, FileFormat, FileLoader, FileMetadata

# Database loader (requires asyncpg)
try:
    from .database_loader import (ConnectionPool, DatabaseConfig,
                                  DatabaseLoader, TransactionManager)

    _HAS_DATABASE_LOADER = True
except ImportError:
    _HAS_DATABASE_LOADER = False
    DatabaseLoader = None
    DatabaseConfig = None
    ConnectionPool = None
    TransactionManager = None

# Cache loader (requires redis)
try:
    from .cache_loader import (CacheConfig, CacheLoader, CacheMetrics,
                               TTLManager)

    _HAS_CACHE_LOADER = True
except ImportError:
    _HAS_CACHE_LOADER = False
    CacheLoader = None
    CacheConfig = None
    CacheMetrics = None
    TTLManager = None

# Archive and export loaders will be implemented as Phase 3 progresses
# from .archive_loader import (
#     ArchiveLoader,
#     ArchivePolicy,
#     RetentionRule,
# )

# from .export_loader import (
#     ExportLoader,
#     ExportFormat,
#     ExportTarget,
# )

# Build __all__ list based on available imports
__all__ = [
    # Base classes (always available)
    "BaseDataLoader",
    "LoadingStrategy",
    "LoadingResult",
    "LoadingMetrics",
    "DataVersion",
    "LoadingError",
    "ValidationError",
    "StorageError",
    # File loader (always available)
    "FileLoader",
    "FileFormat",
    "CompressionType",
    "FileMetadata",
]

# Add database loader if available
if _HAS_DATABASE_LOADER:
    __all__.extend(
        [
            "DatabaseLoader",
            "DatabaseConfig",
            "ConnectionPool",
            "TransactionManager",
        ]
    )

# Add cache loader if available
if _HAS_CACHE_LOADER:
    __all__.extend(
        [
            "CacheLoader",
            "CacheConfig",
            "CacheMetrics",
            "TTLManager",
        ]
    )

# Future components (planned)
# 'ArchiveLoader',
# 'ArchivePolicy',
# 'RetentionRule',
# 'ExportLoader',
# 'ExportFormat',
# 'ExportTarget',

# Version info
__version__ = "1.0.0"
__phase__ = "Phase 3 - Data Loading & Storage"
__status__ = "In Development"
