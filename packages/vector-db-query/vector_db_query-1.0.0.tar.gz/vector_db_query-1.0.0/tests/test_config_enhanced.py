#!/usr/bin/env python3
"""Test the enhanced configuration system."""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from vector_db_query.utils.config_enhanced import (
    Config, ConfigManager, FileFormatConfig, OCRConfig,
    get_config, reset_config
)


def test_file_format_config():
    """Test file format configuration."""
    formats = FileFormatConfig()
    
    # Test default formats
    assert ".pdf" in formats.documents
    assert ".xlsx" in formats.spreadsheets
    assert ".html" in formats.web
    assert ".png" in formats.images
    
    # Test all_supported property
    all_formats = formats.all_supported
    assert isinstance(all_formats, set)
    assert len(all_formats) > 30  # Should have many formats
    
    # Test is_supported method
    assert formats.is_supported(".pdf")
    assert formats.is_supported(".PDF")  # Case insensitive
    assert not formats.is_supported(".xyz")
    
    # Test custom extensions
    formats.custom_extensions = [".custom1", ".custom2"]
    assert formats.is_supported(".custom1")
    assert ".custom1" in formats.all_supported


def test_ocr_config():
    """Test OCR configuration."""
    ocr = OCRConfig()
    
    # Test defaults
    assert ocr.enabled is True
    assert ocr.language == "eng"
    assert ocr.dpi == 300
    assert ocr.confidence_threshold == 60.0
    
    # Test languages property
    assert ocr.languages == "eng"
    
    ocr.additional_languages = ["fra", "deu"]
    assert ocr.languages == "eng+fra+deu"


def test_config_creation():
    """Test creating a full configuration."""
    config = Config()
    
    # Test structure
    assert config.app.name == "Vector DB Query System"
    assert config.paths.data_dir == Path("./data")
    assert config.embedding.model == "embedding-001"
    assert config.document_processing.chunk_size == 1000
    assert config.vector_db.host == "localhost"
    
    # Test nested configs
    assert isinstance(config.document_processing.file_formats, FileFormatConfig)
    assert isinstance(config.document_processing.ocr, OCRConfig)
    
    # Test file format access
    assert ".pdf" in config.document_processing.file_formats.documents


def test_config_save_load():
    """Test saving and loading configuration."""
    config = Config()
    
    # Modify some values
    config.app.log_level = "DEBUG"
    config.document_processing.chunk_size = 2000
    config.document_processing.ocr.language = "fra"
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config.save(Path(f.name))
        temp_path = Path(f.name)
    
    try:
        # Load from file
        loaded_config = Config.load(temp_path)
        
        # Verify values
        assert loaded_config.app.log_level == "DEBUG"
        assert loaded_config.document_processing.chunk_size == 2000
        assert loaded_config.document_processing.ocr.language == "fra"
        
    finally:
        temp_path.unlink()


def test_config_manager():
    """Test configuration manager."""
    # Reset global instance
    reset_config()
    
    # Create temporary config file
    config_data = {
        "app": {"log_level": "WARNING"},
        "document_processing": {
            "chunk_size": 1500,
            "ocr": {"language": "spa"}
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        temp_path = f.name
    
    try:
        # Create manager with custom config
        manager = ConfigManager(temp_path)
        
        # Test get method
        assert manager.get("app.log_level") == "WARNING"
        assert manager.get("document_processing.chunk_size") == 1500
        assert manager.get("document_processing.ocr.language") == "spa"
        assert manager.get("non.existent.key", "default") == "default"
        
        # Test set method
        manager.set("app.log_level", "INFO")
        assert manager.get("app.log_level") == "INFO"
        
    finally:
        Path(temp_path).unlink()


def test_environment_overrides():
    """Test environment variable overrides."""
    # Reset global instance
    reset_config()
    
    # Set environment variables
    os.environ["VECTOR_DB_LOG_LEVEL"] = "ERROR"
    os.environ["CHUNK_SIZE"] = "3000"
    os.environ["OCR_LANGUAGE"] = "deu"
    os.environ["QDRANT_PORT"] = "7333"
    
    try:
        # Get config (will apply env overrides)
        manager = get_config()
        
        # Verify overrides
        assert manager.get("app.log_level") == "ERROR"
        assert manager.get("document_processing.chunk_size") == 3000
        assert manager.get("document_processing.ocr.language") == "deu"
        assert manager.get("vector_db.port") == 7333
        
    finally:
        # Clean up environment
        for key in ["VECTOR_DB_LOG_LEVEL", "CHUNK_SIZE", "OCR_LANGUAGE", "QDRANT_PORT"]:
            os.environ.pop(key, None)
        reset_config()


def test_config_validation():
    """Test configuration validation."""
    manager = get_config()
    
    # Test validation method
    issues = manager.validate()
    # Note: Some issues might exist depending on the environment
    assert isinstance(issues, list)
    
    # Test specific validation scenarios
    manager.config.document_processing.chunk_size = 0
    issues = manager.validate()
    assert any("chunk_size must be positive" in issue for issue in issues)
    
    # Reset to valid value
    manager.config.document_processing.chunk_size = 1000
    
    # Test chunk overlap validation
    manager.config.document_processing.chunk_overlap = 1500
    issues = manager.validate()
    assert any("chunk_overlap must be less than chunk_size" in issue for issue in issues)


def test_config_callbacks():
    """Test configuration change callbacks."""
    manager = get_config()
    
    # Track changes
    changes = []
    
    def callback(key, value):
        changes.append((key, value))
    
    # Subscribe to changes
    manager.subscribe(callback)
    
    # Make changes
    manager.set("app.log_level", "DEBUG")
    manager.set("document_processing.chunk_size", 2500)
    
    # Verify callbacks were called
    assert len(changes) == 2
    assert ("app.log_level", "DEBUG") in changes
    assert ("document_processing.chunk_size", 2500) in changes
    
    # Unsubscribe
    manager.unsubscribe(callback)
    changes.clear()
    
    # Make another change
    manager.set("app.log_level", "INFO")
    
    # Verify callback was not called
    assert len(changes) == 0


def test_export_env():
    """Test exporting configuration as environment variables."""
    manager = get_config()
    
    # Export to env vars
    env_vars = manager.export_env()
    
    # Verify structure
    assert isinstance(env_vars, dict)
    assert "VECTOR_DB_APP_LOG_LEVEL" in env_vars
    assert "VECTOR_DB_DOCUMENT_PROCESSING_CHUNK_SIZE" in env_vars
    assert "VECTOR_DB_VECTOR_DB_HOST" in env_vars
    
    # Verify list handling
    assert "VECTOR_DB_DOCUMENT_PROCESSING_FILE_FORMATS_DOCUMENTS" in env_vars
    # Should be comma-separated
    docs_value = env_vars["VECTOR_DB_DOCUMENT_PROCESSING_FILE_FORMATS_DOCUMENTS"]
    assert ".pdf" in docs_value
    assert "," in docs_value


if __name__ == "__main__":
    # Run tests
    print("Testing Enhanced Configuration System")
    print("="*50)
    
    test_functions = [
        test_file_format_config,
        test_ocr_config,
        test_config_creation,
        test_config_save_load,
        test_config_manager,
        test_environment_overrides,
        test_config_validation,
        test_config_callbacks,
        test_export_env,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            print(f"\nRunning {test_func.__name__}...")
            test_func()
            print(f"✓ {test_func.__name__} passed")
            passed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} failed: {e}")
            failed += 1
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    
    # Always reset at the end
    reset_config()