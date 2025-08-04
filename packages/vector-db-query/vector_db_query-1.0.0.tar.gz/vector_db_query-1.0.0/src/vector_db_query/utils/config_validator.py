"""Configuration validators for Vector DB Query System."""

from typing import Any, Dict, List, Optional, Set
import re
from pathlib import Path

from pydantic import ValidationError


class ConfigValidator:
    """Validates configuration settings."""
    
    def __init__(self):
        """Initialize the configuration validator."""
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate(self, config_dict: Dict[str, Any]) -> bool:
        """Validate entire configuration.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            True if valid, False otherwise
        """
        self.errors = []
        self.warnings = []
        
        # Validate each section
        self._validate_paths(config_dict.get("paths", {}))
        self._validate_document_processing(config_dict.get("document_processing", {}))
        self._validate_embedding(config_dict.get("embedding", {}))
        self._validate_vector_db(config_dict.get("vector_db", {}))
        self._validate_format_settings(config_dict.get("document_processing", {}).get("format_settings", {}))
        
        return len(self.errors) == 0
        
    def _validate_paths(self, paths: Dict[str, Any]) -> None:
        """Validate path settings."""
        for key, path in paths.items():
            if isinstance(path, str):
                path_obj = Path(path)
                # Check if parent directory exists for writable paths
                if key in ["data_dir", "log_dir", "temp_dir"]:
                    parent = path_obj.parent
                    if parent.exists() and not parent.is_dir():
                        self.errors.append(f"Parent of {key} '{path}' exists but is not a directory")
                    elif not parent.exists():
                        self.warnings.append(f"Parent directory of {key} '{path}' does not exist")
                        
    def _validate_document_processing(self, doc_proc: Dict[str, Any]) -> None:
        """Validate document processing settings."""
        # Validate chunk settings
        chunk_size = doc_proc.get("chunk_size", 1000)
        chunk_overlap = doc_proc.get("chunk_overlap", 200)
        
        if chunk_size <= 0:
            self.errors.append(f"chunk_size must be positive, got {chunk_size}")
        if chunk_overlap < 0:
            self.errors.append(f"chunk_overlap must be non-negative, got {chunk_overlap}")
        if chunk_overlap >= chunk_size:
            self.errors.append(f"chunk_overlap ({chunk_overlap}) must be less than chunk_size ({chunk_size})")
            
        # Validate chunking strategy
        strategy = doc_proc.get("chunking_strategy", "sliding_window")
        valid_strategies = ["sliding_window", "semantic"]
        if strategy not in valid_strategies:
            self.errors.append(f"Invalid chunking_strategy '{strategy}', must be one of {valid_strategies}")
            
        # Validate scanner settings
        scanner = doc_proc.get("scanner", {})
        max_file_size = scanner.get("max_file_size_mb", 100)
        if max_file_size <= 0:
            self.errors.append(f"max_file_size_mb must be positive, got {max_file_size}")
            
    def _validate_embedding(self, embedding: Dict[str, Any]) -> None:
        """Validate embedding settings."""
        # Validate dimensions
        dimensions = embedding.get("dimensions", 768)
        valid_dimensions = [768, 1536, 3072]
        if dimensions not in valid_dimensions:
            self.errors.append(f"Invalid embedding dimensions {dimensions}, must be one of {valid_dimensions}")
            
        # Validate model
        model = embedding.get("model", "")
        if not model:
            self.errors.append("Embedding model must be specified")
            
        # Validate batch size
        batch_size = embedding.get("batch_size", 100)
        if batch_size <= 0:
            self.errors.append(f"batch_size must be positive, got {batch_size}")
            
    def _validate_vector_db(self, vector_db: Dict[str, Any]) -> None:
        """Validate vector database settings."""
        # Validate distance metric
        metric = vector_db.get("distance_metric", "cosine")
        valid_metrics = ["cosine", "euclidean", "dot"]
        if metric not in valid_metrics:
            self.errors.append(f"Invalid distance_metric '{metric}', must be one of {valid_metrics}")
            
        # Validate ports
        port = vector_db.get("port", 6333)
        grpc_port = vector_db.get("grpc_port", 6334)
        
        if not (1 <= port <= 65535):
            self.errors.append(f"Invalid port {port}, must be between 1 and 65535")
        if not (1 <= grpc_port <= 65535):
            self.errors.append(f"Invalid grpc_port {grpc_port}, must be between 1 and 65535")
        if port == grpc_port:
            self.errors.append(f"port and grpc_port cannot be the same ({port})")
            
    def _validate_format_settings(self, format_settings: Dict[str, Any]) -> None:
        """Validate format-specific settings."""
        # Validate Excel settings
        excel = format_settings.get("excel", {})
        max_rows = excel.get("max_rows_per_sheet", 10000)
        if max_rows <= 0:
            self.errors.append(f"Excel max_rows_per_sheet must be positive, got {max_rows}")
            
        # Validate Log settings
        logs = format_settings.get("logs", {})
        max_lines = logs.get("max_lines", 10000)
        if max_lines <= 0:
            self.errors.append(f"Log max_lines must be positive, got {max_lines}")
            
        # Validate OCR settings
        ocr = format_settings.get("ocr", {})
        confidence = ocr.get("confidence_threshold", 60.0)
        if not (0 <= confidence <= 100):
            self.errors.append(f"OCR confidence_threshold must be between 0 and 100, got {confidence}")
            
        dpi = ocr.get("dpi", 300)
        if dpi <= 0:
            self.errors.append(f"OCR dpi must be positive, got {dpi}")
            
        # Validate language code
        language = ocr.get("language", "eng")
        if not re.match(r'^[a-z]{3}$', language):
            self.warnings.append(f"OCR language '{language}' may not be a valid ISO 639-2 code")
            
    def get_errors(self) -> List[str]:
        """Get validation errors."""
        return self.errors
        
    def get_warnings(self) -> List[str]:
        """Get validation warnings."""
        return self.warnings
        
    def format_report(self) -> str:
        """Format validation report."""
        report = []
        
        if self.errors:
            report.append("ERRORS:")
            for error in self.errors:
                report.append(f"  ✗ {error}")
                
        if self.warnings:
            if report:
                report.append("")
            report.append("WARNINGS:")
            for warning in self.warnings:
                report.append(f"  ⚠ {warning}")
                
        if not self.errors and not self.warnings:
            report.append("✓ Configuration is valid")
            
        return "\n".join(report)


def validate_config_file(config_path: Path) -> bool:
    """Validate a configuration file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        True if valid, False otherwise
    """
    import yaml
    
    validator = ConfigValidator()
    
    try:
        with open(config_path, 'r') as f:
            config_dict = yaml.safe_load(f)
            
        is_valid = validator.validate(config_dict)
        print(validator.format_report())
        
        return is_valid
        
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return False


if __name__ == "__main__":
    # Test validator with default config
    import sys
    
    if len(sys.argv) > 1:
        config_file = Path(sys.argv[1])
    else:
        config_file = Path(__file__).parent.parent.parent.parent / "config" / "default.yaml"
        
    if validate_config_file(config_file):
        sys.exit(0)
    else:
        sys.exit(1)