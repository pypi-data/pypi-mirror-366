"""Basic tests to verify installation."""

import pytest
from pathlib import Path


def test_package_import():
    """Test that the package can be imported."""
    import vector_db_query
    assert vector_db_query.__version__ == "1.0.0"


def test_cli_entry_point():
    """Test that CLI entry point exists."""
    from vector_db_query.__main__ import main
    assert callable(main)


def test_config_loading():
    """Test that config can be loaded."""
    from vector_db_query.utils.config import Config
    config = Config()
    assert config is not None


def test_document_processor_import():
    """Test document processor imports."""
    from vector_db_query.document_processor import DocumentProcessor
    assert DocumentProcessor is not None


def test_vector_db_import():
    """Test vector DB imports."""
    from vector_db_query.vector_db import VectorDBService
    assert VectorDBService is not None