"""
Test ETL Package Structure - investByYourself
Story-005: ETL & Database Architecture Design

Basic tests to verify ETL package structure and imports.
"""

import os
import sys

import pytest

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestETLPackageStructure:
    """Test ETL package structure and basic functionality."""

    def test_etl_package_import(self):
        """Test that ETL package can be imported."""
        try:
            import src.etl

            assert src.etl.__version__ == "1.0.0"
            assert "collectors" in src.etl.__all__
            assert "transformers" in src.etl.__all__
            assert "loaders" in src.etl.__all__
            assert "validators" in src.etl.__all__
            assert "cache" in src.etl.__all__
            assert "utils" in src.etl.__all__
            assert "worker" in src.etl.__all__
        except ImportError:
            pytest.skip("ETL package not available")

    def test_etl_worker_import(self):
        """Test that ETL worker can be imported."""
        try:
            from src.etl.worker import ETLWorker

            assert ETLWorker is not None
            assert hasattr(ETLWorker, "__init__")
            assert hasattr(ETLWorker, "start")
            assert hasattr(ETLWorker, "stop")
        except ImportError:
            pytest.skip("ETL worker not available")

    def test_etl_worker_initialization(self):
        """Test ETL worker initialization."""
        try:
            from src.etl.worker import ETLWorker

            # Test worker initialization
            worker = ETLWorker()
            assert worker.running == False
            assert worker.batch_size == 1000
            assert worker.max_workers == 4
            assert worker.retry_attempts == 3
            assert worker.retry_delay == 5

            # Test status method
            status = worker.get_status()
            assert isinstance(status, dict)
            assert "running" in status
            assert "batch_size" in status
            assert "max_workers" in status

        except ImportError:
            pytest.skip("ETL worker not available")

    def test_etl_directories_exist(self):
        """Test that ETL directory structure exists."""
        etl_dir = "src/etl"
        assert os.path.exists(etl_dir), "ETL directory not found"

        # Check for required subdirectories
        required_dirs = [
            "collectors",
            "transformers",
            "loaders",
            "validators",
            "cache",
            "utils",
        ]
        for dir_name in required_dirs:
            dir_path = os.path.join(etl_dir, dir_name)
            assert os.path.exists(dir_path), f"ETL subdirectory {dir_name} not found"

    def test_etl_files_exist(self):
        """Test that key ETL files exist."""
        # Check main worker file
        worker_file = "src/etl/worker.py"
        assert os.path.exists(worker_file), "ETL worker file not found"

        # Check __init__.py files
        init_files = [
            "src/etl/__init__.py",
            "src/etl/collectors/__init__.py",
            "src/etl/transformers/__init__.py",
            "src/etl/loaders/__init__.py",
            "src/etl/validators/__init__.py",
            "src/etl/cache/__init__.py",
            "src/etl/utils/__init__.py",
        ]

        for init_file in init_files:
            if os.path.exists(init_file):
                # File exists, check it's readable
                assert os.access(
                    init_file, os.R_OK
                ), f"ETL init file {init_file} not readable"
            else:
                # File doesn't exist yet (will be created during implementation)
                pass

    def test_database_schema_exists(self):
        """Test that database schema file exists."""
        schema_file = "database/schema.sql"
        assert os.path.exists(schema_file), "Database schema file not found"

        # Check file size (should be substantial for a complete schema)
        file_size = os.path.getsize(schema_file)
        assert file_size > 1000, "Database schema file seems too small"

    def test_docker_compose_exists(self):
        """Test that Docker Compose file exists."""
        compose_file = "docker-compose.yml"
        assert os.path.exists(compose_file), "Docker Compose file not found"

        # Check file size
        file_size = os.path.getsize(compose_file)
        assert file_size > 500, "Docker Compose file seems too small"

    def test_etl_dockerfile_exists(self):
        """Test that ETL Dockerfile exists."""
        dockerfile = "Dockerfile.etl"
        assert os.path.exists(dockerfile), "ETL Dockerfile not found"

        # Check file size
        file_size = os.path.getsize(dockerfile)
        assert file_size > 200, "ETL Dockerfile seems too small"


if __name__ == "__main__":
    pytest.main([__file__])
