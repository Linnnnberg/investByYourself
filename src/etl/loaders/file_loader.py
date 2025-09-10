"""
File Data Loader - Support for CSV, JSON, Parquet with compression and versioning

This module provides file-based data loading capabilities including:
- Multiple file format support (CSV, JSON, Parquet)
- Compression options (gzip, bzip2, lz4)
- File versioning and metadata tracking
- Incremental file loading
- Directory organization and cleanup

Author: investByYourself Development Team
Created: August 2025
Phase: Tech-009 Phase 3 - Data Loading & Storage
"""

import bz2
import csv
import gzip
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import structlog

from .base_loader import (BaseDataLoader, DataVersion, LoadingError,
                          LoadingMetrics, LoadingResult, LoadingStrategy,
                          StorageError, ValidationError)

# Configure structured logging
logger = structlog.get_logger(__name__)


class FileFormat(Enum):
    """Supported file formats."""

    CSV = "csv"
    JSON = "json"
    JSONL = "jsonl"  # JSON Lines
    PARQUET = "parquet"
    TSV = "tsv"


class CompressionType(Enum):
    """Supported compression types."""

    NONE = None
    GZIP = "gzip"
    BZIP2 = "bzip2"
    LZ4 = "lz4"


@dataclass
class FileMetadata:
    """Metadata for file tracking."""

    file_path: str
    file_format: FileFormat
    compression: CompressionType
    size_bytes: int
    checksum: str
    record_count: int
    created_at: datetime
    version_id: str
    schema_version: str = "1.0"
    tags: Dict[str, str] = field(default_factory=dict)


class FileLoader(BaseDataLoader):
    """
    File-based data loader with support for multiple formats and compression.

    Features:
    - Multiple file formats (CSV, JSON, Parquet)
    - Compression support
    - File versioning and organization
    - Incremental loading
    - Metadata tracking
    - Directory cleanup and archiving
    """

    def __init__(
        self,
        base_path: str = "data",
        file_format: FileFormat = FileFormat.JSON,
        compression: CompressionType = CompressionType.GZIP,
        create_subdirectories: bool = True,
        **kwargs,
    ):
        """
        Initialize the file loader.

        Args:
            base_path: Base directory for file storage
            file_format: Default file format
            compression: Default compression type
            create_subdirectories: Whether to create date-based subdirectories
            **kwargs: Additional base loader parameters
        """
        super().__init__(loader_id="file_loader", **kwargs)

        self.base_path = Path(base_path)
        self.file_format = file_format
        self.compression = compression
        self.create_subdirectories = create_subdirectories

        # File organization
        self.current_session_path = None
        self.metadata_store: Dict[str, FileMetadata] = {}

        self.logger = logger.bind(loader_id=self.loader_id)

    async def connect(self) -> None:
        """Initialize file storage directories."""
        try:
            # Create base directory
            self.base_path.mkdir(parents=True, exist_ok=True)

            # Create session-specific directory if needed
            if self.create_subdirectories:
                session_name = datetime.now().strftime("%Y%m%d_%H%M%S")
                self.current_session_path = self.base_path / session_name
                self.current_session_path.mkdir(parents=True, exist_ok=True)
            else:
                self.current_session_path = self.base_path

            # Create metadata directory
            metadata_dir = self.base_path / "metadata"
            metadata_dir.mkdir(exist_ok=True)

            self.is_connected = True
            self.logger.info(
                "File loader initialized",
                base_path=str(self.base_path),
                session_path=str(self.current_session_path),
            )

        except Exception as e:
            self.logger.error("Failed to initialize file loader", error=str(e))
            raise StorageError(f"Failed to initialize file loader: {e}")

    async def disconnect(self) -> None:
        """Cleanup file loader resources."""
        try:
            # Save metadata
            if self.metadata_store:
                await self._save_metadata()

            self.is_connected = False
            self.logger.info("File loader disconnected")

        except Exception as e:
            self.logger.error("Error during disconnect", error=str(e))

    async def load_data(
        self,
        data: Union[List[Dict[str, Any]], Dict[str, Any]],
        strategy: LoadingStrategy = LoadingStrategy.APPEND,
        target_table: Optional[str] = None,
        file_format: Optional[FileFormat] = None,
        compression: Optional[CompressionType] = None,
        **kwargs,
    ) -> LoadingResult:
        """
        Load data to files using the specified strategy.

        Args:
            data: Data to load
            strategy: Loading strategy to use
            target_table: Target file prefix/name
            file_format: File format override
            compression: Compression override
            **kwargs: Additional parameters

        Returns:
            LoadingResult with metrics and status
        """
        if not self.is_connected:
            raise StorageError("File loader not connected")

        # Normalize data to list
        if isinstance(data, dict):
            data = [data]

        if not data:
            return LoadingResult(
                success=True, metrics=LoadingMetrics(start_time=datetime.now())
            )

        # Use provided format/compression or defaults
        file_format = file_format or self.file_format
        compression = compression or self.compression

        # Initialize metrics
        self.metrics = LoadingMetrics(start_time=datetime.now())
        result = LoadingResult(success=True, metrics=self.metrics)

        try:
            # Generate file path
            file_path = self._generate_file_path(target_table, file_format, compression)

            # Load data based on strategy
            if strategy == LoadingStrategy.REPLACE:
                await self._write_file(
                    data, file_path, file_format, compression, mode="w"
                )
            elif strategy == LoadingStrategy.APPEND:
                await self._write_file(
                    data, file_path, file_format, compression, mode="a"
                )
            elif strategy == LoadingStrategy.INCREMENTAL:
                await self._write_incremental(data, file_path, file_format, compression)
            else:
                raise ValueError(f"Unsupported loading strategy for files: {strategy}")

            # Create file metadata
            metadata = await self._create_file_metadata(
                file_path, file_format, compression, len(data)
            )

            # Create data version if versioning enabled
            if self.enable_versioning:
                checksum = self.calculate_checksum(data)
                data_version = await self.create_data_version(
                    str(file_path),
                    len(data),
                    checksum,
                    {"file_metadata": metadata.__dict__},
                )
                result.data_version = data_version

            # Update metrics
            self.metrics.records_processed = len(data)
            self.metrics.records_inserted = len(data)

        except Exception as e:
            self.logger.error("Error during file loading", error=str(e))
            result.success = False
            result.add_error(f"File loading failed: {str(e)}")

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
        """Load a batch of records to file."""
        # For file loading, we don't need separate batch processing
        # since we write entire datasets at once
        return LoadingResult(
            success=True, metrics=LoadingMetrics(start_time=datetime.now())
        )

    async def _write_file(
        self,
        data: List[Dict[str, Any]],
        file_path: Path,
        file_format: FileFormat,
        compression: CompressionType,
        mode: str = "w",
    ) -> None:
        """Write data to file with specified format and compression."""

        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Open file with appropriate compression
        file_opener = self._get_file_opener(compression)

        try:
            with file_opener(file_path, mode + "t", encoding="utf-8") as f:
                if file_format == FileFormat.JSON:
                    if mode == "w":
                        json.dump(data, f, indent=2, default=str)
                    else:  # append mode
                        for record in data:
                            json.dump(record, f, default=str)
                            f.write("\n")

                elif file_format == FileFormat.JSONL:
                    for record in data:
                        json.dump(record, f, default=str)
                        f.write("\n")

                elif file_format in [FileFormat.CSV, FileFormat.TSV]:
                    delimiter = "\t" if file_format == FileFormat.TSV else ","

                    # Check if file exists and has headers for append mode
                    write_headers = (
                        mode == "w"
                        or not file_path.exists()
                        or file_path.stat().st_size == 0
                    )

                    if data:
                        fieldnames = list(data[0].keys())
                        writer = csv.DictWriter(
                            f, fieldnames=fieldnames, delimiter=delimiter
                        )

                        if write_headers:
                            writer.writeheader()

                        writer.writerows(data)

                elif file_format == FileFormat.PARQUET:
                    # For Parquet, we'd need pandas and pyarrow
                    # This is a placeholder for future implementation
                    raise NotImplementedError("Parquet format not yet implemented")

                else:
                    raise ValueError(f"Unsupported file format: {file_format}")

        except Exception as e:
            self.logger.error(
                "Failed to write file", file_path=str(file_path), error=str(e)
            )
            raise StorageError(f"Failed to write file {file_path}: {e}")

    async def _write_incremental(
        self,
        data: List[Dict[str, Any]],
        file_path: Path,
        file_format: FileFormat,
        compression: CompressionType,
    ) -> None:
        """Write data incrementally, checking for existing records."""

        existing_data = []

        # Read existing data if file exists
        if file_path.exists():
            try:
                existing_data = await self._read_file(
                    file_path, file_format, compression
                )
            except Exception as e:
                self.logger.warning(
                    "Failed to read existing file for incremental load", error=str(e)
                )

        # Create a set of existing record checksums for deduplication
        existing_checksums = set()
        if existing_data:
            for record in existing_data:
                record_checksum = self.calculate_checksum(record)
                existing_checksums.add(record_checksum)

        # Filter out duplicate records
        new_records = []
        for record in data:
            record_checksum = self.calculate_checksum(record)
            if record_checksum not in existing_checksums:
                new_records.append(record)

        # Write new records only
        if new_records:
            await self._write_file(
                new_records, file_path, file_format, compression, mode="a"
            )
            self.logger.info(
                "Incremental load completed",
                total_records=len(data),
                new_records=len(new_records),
                skipped_duplicates=len(data) - len(new_records),
            )
        else:
            self.logger.info("No new records to write in incremental load")

    async def _read_file(
        self, file_path: Path, file_format: FileFormat, compression: CompressionType
    ) -> List[Dict[str, Any]]:
        """Read data from file."""

        file_opener = self._get_file_opener(compression)
        data = []

        try:
            with file_opener(file_path, "rt", encoding="utf-8") as f:
                if file_format == FileFormat.JSON:
                    data = json.load(f)
                    if not isinstance(data, list):
                        data = [data]

                elif file_format == FileFormat.JSONL:
                    for line in f:
                        if line.strip():
                            data.append(json.loads(line))

                elif file_format in [FileFormat.CSV, FileFormat.TSV]:
                    delimiter = "\t" if file_format == FileFormat.TSV else ","
                    reader = csv.DictReader(f, delimiter=delimiter)
                    data = list(reader)

                else:
                    raise ValueError(
                        f"Unsupported file format for reading: {file_format}"
                    )

        except Exception as e:
            self.logger.error(
                "Failed to read file", file_path=str(file_path), error=str(e)
            )
            raise StorageError(f"Failed to read file {file_path}: {e}")

        return data

    def _get_file_opener(self, compression: CompressionType):
        """Get appropriate file opener based on compression."""
        if compression == CompressionType.GZIP:
            return gzip.open
        elif compression == CompressionType.BZIP2:
            return bz2.open
        elif compression == CompressionType.LZ4:
            try:
                import lz4.frame

                return lz4.frame.open
            except ImportError:
                self.logger.warning("LZ4 not available, falling back to no compression")
                return open
        else:
            return open

    def _generate_file_path(
        self,
        target: Optional[str],
        file_format: FileFormat,
        compression: CompressionType,
    ) -> Path:
        """Generate file path based on target and format."""

        # Generate base filename
        if target:
            filename = target
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data_{timestamp}"

        # Add file extension
        extension = file_format.value
        if compression and compression != CompressionType.NONE:
            extension += f".{compression.value}"

        filename = f"{filename}.{extension}"

        return self.current_session_path / filename

    async def _create_file_metadata(
        self,
        file_path: Path,
        file_format: FileFormat,
        compression: CompressionType,
        record_count: int,
    ) -> FileMetadata:
        """Create metadata for the file."""
        import uuid

        # Calculate file size and checksum
        size_bytes = file_path.stat().st_size

        # Calculate file checksum
        import hashlib

        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        file_checksum = hash_md5.hexdigest()

        metadata = FileMetadata(
            file_path=str(file_path),
            file_format=file_format,
            compression=compression,
            size_bytes=size_bytes,
            checksum=file_checksum,
            record_count=record_count,
            created_at=datetime.now(),
            version_id=str(uuid.uuid4()),
        )

        # Store metadata
        self.metadata_store[str(file_path)] = metadata

        return metadata

    async def _save_metadata(self) -> None:
        """Save metadata to file."""
        metadata_file = self.base_path / "metadata" / "file_metadata.json"

        try:
            # Convert metadata to serializable format
            serializable_metadata = {}
            for path, metadata in self.metadata_store.items():
                serializable_metadata[path] = {
                    "file_path": metadata.file_path,
                    "file_format": metadata.file_format.value,
                    "compression": (
                        metadata.compression.value if metadata.compression else None
                    ),
                    "size_bytes": metadata.size_bytes,
                    "checksum": metadata.checksum,
                    "record_count": metadata.record_count,
                    "created_at": metadata.created_at.isoformat(),
                    "version_id": metadata.version_id,
                    "schema_version": metadata.schema_version,
                    "tags": metadata.tags,
                }

            with open(metadata_file, "w") as f:
                json.dump(serializable_metadata, f, indent=2)

            self.logger.info("Metadata saved", metadata_file=str(metadata_file))

        except Exception as e:
            self.logger.error("Failed to save metadata", error=str(e))

    async def get_data_version(self, target: str) -> Optional[DataVersion]:
        """Get the current data version for a target file."""
        # For file loader, we check the metadata store
        metadata = self.metadata_store.get(target)

        if metadata:
            return DataVersion(
                version_id=metadata.version_id,
                timestamp=metadata.created_at,
                checksum=metadata.checksum,
                record_count=metadata.record_count,
                schema_version=metadata.schema_version,
                source=self.loader_id,
                metadata={
                    "file_path": metadata.file_path,
                    "file_format": metadata.file_format.value,
                    "compression": (
                        metadata.compression.value if metadata.compression else None
                    ),
                    "size_bytes": metadata.size_bytes,
                },
            )

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

        self.logger.info(
            "Created data version", version_id=version.version_id, target=target
        )
        return version

    async def optimize_storage(self, target: str) -> Dict[str, Any]:
        """Optimize file storage (placeholder for compression analysis)."""
        try:
            file_path = Path(target)
            if file_path.exists():
                size_bytes = file_path.stat().st_size

                return {
                    "status": "analyzed",
                    "target": target,
                    "size_bytes": size_bytes,
                    "size_human": f"{size_bytes / 1024 / 1024:.2f} MB",
                    "compression_recommendation": (
                        "gzip" if size_bytes > 1024 * 1024 else "none"
                    ),
                }
            else:
                return {"status": "file_not_found", "target": target}

        except Exception as e:
            return {"status": "failed", "target": target, "error": str(e)}

    async def get_statistics(self, target: str) -> Dict[str, Any]:
        """Get file statistics."""
        try:
            file_path = Path(target)
            if file_path.exists():
                stat = file_path.stat()
                metadata = self.metadata_store.get(target, None)

                return {
                    "file": target,
                    "size_bytes": stat.st_size,
                    "size_human": f"{stat.st_size / 1024 / 1024:.2f} MB",
                    "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "record_count": metadata.record_count if metadata else "unknown",
                    "file_format": (
                        metadata.file_format.value if metadata else "unknown"
                    ),
                    "compression": (
                        metadata.compression.value
                        if metadata and metadata.compression
                        else "none"
                    ),
                }
            else:
                return {"status": "file_not_found", "target": target}

        except Exception as e:
            return {"status": "failed", "target": target, "error": str(e)}
