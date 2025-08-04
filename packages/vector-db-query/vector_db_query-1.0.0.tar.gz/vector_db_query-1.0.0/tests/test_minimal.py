"""Minimal tests that work without complex dependencies."""

import pytest


def test_package_version():
    """Test that the package has a version."""
    import vector_db_query
    assert hasattr(vector_db_query, '__version__')
    assert vector_db_query.__version__ == "1.0.0"


def test_utils_config():
    """Test that config can be loaded."""
    from vector_db_query.utils.config import Config
    config = Config()
    assert config is not None


def test_basic_imports():
    """Test basic module imports."""
    # These should not fail
    import vector_db_query
    import vector_db_query.utils
    import vector_db_query.document_processor
    import vector_db_query.vector_db
    assert True  # If we get here, imports worked