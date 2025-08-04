"""Enhanced configuration management for Vector DB Query System with file format support."""

import os
from pathlib import Path
from typing import Any, Dict, Optional, List, Set

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError, validator


class AppConfig(BaseModel):
    """Application configuration."""
    
    name: str = Field(default="Vector DB Query System")
    version: str = Field(default="1.0.0")
    log_level: str = Field(default="INFO")


class PathsConfig(BaseModel):
    """Paths configuration."""
    
    data_dir: Path = Field(default=Path("./data"))
    log_dir: Path = Field(default=Path("./logs"))
    config_dir: Path = Field(default=Path("./config"))
    temp_dir: Path = Field(default=Path("./temp"))
    
    @validator('*', pre=True)
    def convert_to_path(cls, v):
        """Convert string paths to Path objects."""
        if isinstance(v, str):
            return Path(v)
        return v


class FileFormatConfig(BaseModel):
    """File format configuration."""
    
    # Document formats
    documents: List[str] = Field(default_factory=lambda: [
        ".pdf", ".doc", ".docx", ".txt", ".md", ".markdown", ".rtf", ".odt"
    ])
    
    # Spreadsheet formats
    spreadsheets: List[str] = Field(default_factory=lambda: [
        ".xlsx", ".xls", ".csv", ".ods"
    ])
    
    # Presentation formats
    presentations: List[str] = Field(default_factory=lambda: [
        ".pptx", ".ppt", ".odp"
    ])
    
    # Email formats
    email: List[str] = Field(default_factory=lambda: [
        ".eml", ".mbox", ".msg"
    ])
    
    # Web formats
    web: List[str] = Field(default_factory=lambda: [
        ".html", ".htm", ".xhtml", ".xml"
    ])
    
    # Configuration formats
    config: List[str] = Field(default_factory=lambda: [
        ".json", ".yaml", ".yml", ".ini", ".cfg", ".conf", ".config", ".toml"
    ])
    
    # Image formats (for OCR)
    images: List[str] = Field(default_factory=lambda: [
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif", ".webp"
    ])
    
    # Log formats
    logs: List[str] = Field(default_factory=lambda: [".log"])
    
    # Data formats
    data: List[str] = Field(default_factory=lambda: [
        ".geojson", ".jsonl", ".ndjson"
    ])
    
    # Archive formats
    archives: List[str] = Field(default_factory=lambda: [
        ".zip", ".tar", ".tar.gz", ".tar.bz2", ".tar.xz", ".7z"
    ])
    
    # Custom extensions
    custom_extensions: List[str] = Field(default_factory=list)
    
    @property
    def all_supported(self) -> Set[str]:
        """Get all supported file extensions."""
        all_extensions = set()
        for field_name, field_value in self:
            if field_name != "custom_extensions" and isinstance(field_value, list):
                all_extensions.update(field_value)
        all_extensions.update(self.custom_extensions)
        return all_extensions
    
    def is_supported(self, extension: str) -> bool:
        """Check if a file extension is supported."""
        return extension.lower() in self.all_supported


class OCRConfig(BaseModel):
    """OCR configuration."""
    
    enabled: bool = Field(default=True)
    language: str = Field(default="eng")
    additional_languages: List[str] = Field(default_factory=list)
    dpi: int = Field(default=300)
    preprocessing: bool = Field(default=True)
    timeout: int = Field(default=30)
    confidence_threshold: float = Field(default=60.0)
    tesseract_cmd: Optional[str] = Field(default=None)
    
    @property
    def languages(self) -> str:
        """Get combined language string for Tesseract."""
        langs = [self.language] + self.additional_languages
        return "+".join(langs)


class EmbeddingConfig(BaseModel):
    """Embedding configuration."""
    
    model: str = Field(default="embedding-001")
    dimensions: int = Field(default=768)
    task_type: str = Field(default="RETRIEVAL_DOCUMENT")
    batch_size: int = Field(default=100)
    max_retries: int = Field(default=3)
    retry_delay: float = Field(default=1.0)


class FormatSettings(BaseModel):
    """Format-specific processing settings."""
    
    class ExcelSettings(BaseModel):
        """Excel-specific settings."""
        extract_formulas: bool = Field(default=True)
        extract_comments: bool = Field(default=True)
        process_all_sheets: bool = Field(default=True)
        max_rows_per_sheet: int = Field(default=10000)
    
    class PowerPointSettings(BaseModel):
        """PowerPoint-specific settings."""
        extract_speaker_notes: bool = Field(default=True)
        extract_slide_numbers: bool = Field(default=True)
        include_master_slides: bool = Field(default=False)
    
    class EmailSettings(BaseModel):
        """Email-specific settings."""
        extract_attachments: bool = Field(default=True)
        thread_detection: bool = Field(default=True)
        sanitize_content: bool = Field(default=True)
        include_headers: bool = Field(default=True)
    
    class HTMLSettings(BaseModel):
        """HTML-specific settings."""
        remove_scripts: bool = Field(default=True)
        remove_styles: bool = Field(default=True)
        convert_to_markdown: bool = Field(default=False)
        preserve_links: bool = Field(default=True)
    
    class ConfigFileSettings(BaseModel):
        """Configuration file settings."""
        preserve_structure: bool = Field(default=True)
        include_comments: bool = Field(default=True)
        validate_syntax: bool = Field(default=True)
    
    class LogSettings(BaseModel):
        """Log file settings."""
        summarize: bool = Field(default=True)
        extract_patterns: bool = Field(default=True)
        max_lines: int = Field(default=10000)
    
    excel: ExcelSettings = Field(default_factory=ExcelSettings)
    powerpoint: PowerPointSettings = Field(default_factory=PowerPointSettings)
    email: EmailSettings = Field(default_factory=EmailSettings)
    html: HTMLSettings = Field(default_factory=HTMLSettings)
    config_files: ConfigFileSettings = Field(default_factory=ConfigFileSettings)
    logs: LogSettings = Field(default_factory=LogSettings)


class DocumentProcessingConfig(BaseModel):
    """Document processing configuration."""
    
    # Chunking settings
    chunk_size: int = Field(default=1000)
    chunk_overlap: int = Field(default=200)
    chunking_strategy: str = Field(default="sliding_window")
    
    # Scanner settings
    class ScannerSettings(BaseModel):
        """File scanner settings."""
        max_file_size_mb: float = Field(default=100.0)
        ignored_patterns: List[str] = Field(default_factory=lambda: [".*", "__pycache__"])
    
    # Processing settings
    encoding: str = Field(default="utf-8")
    max_file_size_mb: int = Field(default=100)
    extract_metadata: bool = Field(default=True)
    extract_tables: bool = Field(default=True)
    preserve_formatting: bool = Field(default=False)
    
    # Language settings
    detect_language: bool = Field(default=True)
    supported_languages: List[str] = Field(default_factory=lambda: ["en", "es", "fr", "de", "it"])
    
    # Performance settings
    parallel_processing: bool = Field(default=True)
    max_workers: int = Field(default=4)
    memory_limit_mb: int = Field(default=1024)
    
    # File format settings
    file_formats: FileFormatConfig = Field(default_factory=FileFormatConfig)
    ocr: OCRConfig = Field(default_factory=OCRConfig)
    scanner: ScannerSettings = Field(default_factory=ScannerSettings)
    format_settings: FormatSettings = Field(default_factory=FormatSettings)


class VectorDBConfig(BaseModel):
    """Vector database configuration."""
    
    type: str = Field(default="qdrant")
    host: str = Field(default="localhost")
    port: int = Field(default=6333)
    grpc_port: int = Field(default=6334)
    collection_name: str = Field(default="documents")
    distance_metric: str = Field(default="cosine")
    vector_size: int = Field(default=768)
    timeout: int = Field(default=30)
    
    # Advanced settings
    shard_number: int = Field(default=1)
    replication_factor: int = Field(default=1)
    write_consistency_factor: int = Field(default=1)
    on_disk_payload: bool = Field(default=False)
    
    # Connection pool settings
    pool_size: int = Field(default=10)
    pool_timeout: int = Field(default=10)


class MCPConfig(BaseModel):
    """MCP configuration."""
    
    server_host: str = Field(default="localhost")
    server_port: int = Field(default=5000)
    max_context_length: int = Field(default=100000)
    tools: list[Dict[str, str]] = Field(default_factory=list)
    
    # Security settings
    auth_enabled: bool = Field(default=True)
    tls_enabled: bool = Field(default=False)
    cert_path: Optional[str] = Field(default=None)
    key_path: Optional[str] = Field(default=None)
    
    # Rate limiting
    rate_limit_enabled: bool = Field(default=True)
    requests_per_minute: int = Field(default=60)
    burst_size: int = Field(default=10)


class CLIConfig(BaseModel):
    """CLI configuration."""
    
    theme: str = Field(default="default")
    page_size: int = Field(default=10)
    confirm_actions: bool = Field(default=True)
    show_progress: bool = Field(default=True)
    interactive_mode: bool = Field(default=True)
    
    # Output settings
    output_format: str = Field(default="rich")  # rich, plain, json
    color_enabled: bool = Field(default=True)
    unicode_enabled: bool = Field(default=True)
    
    # Progress bar settings
    progress_bar_style: str = Field(default="default")
    show_eta: bool = Field(default=True)
    show_speed: bool = Field(default=True)


class QueryConfig(BaseModel):
    """Query configuration."""
    
    default_limit: int = Field(default=10)
    max_limit: int = Field(default=100)
    score_threshold: float = Field(default=0.7)
    include_metadata: bool = Field(default=True)
    
    # Advanced query settings
    use_reranking: bool = Field(default=False)
    reranking_model: Optional[str] = Field(default=None)
    hybrid_search: bool = Field(default=False)
    keyword_weight: float = Field(default=0.3)
    
    # Result settings
    highlight_matches: bool = Field(default=True)
    include_scores: bool = Field(default=True)
    include_vectors: bool = Field(default=False)


class LoggingConfig(BaseModel):
    """Logging configuration."""
    
    format: str = Field(default="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")
    date_format: str = Field(default="%Y-%m-%d %H:%M:%S")
    file_max_bytes: int = Field(default=10485760)
    file_backup_count: int = Field(default=5)
    
    # Advanced logging
    log_to_file: bool = Field(default=True)
    log_to_console: bool = Field(default=True)
    json_logs: bool = Field(default=False)
    include_traceback: bool = Field(default=True)
    
    # Log levels per module
    module_levels: Dict[str, str] = Field(default_factory=dict)


class MonitoringConfig(BaseModel):
    """Monitoring configuration."""
    
    enabled: bool = Field(default=True)
    metrics_port: int = Field(default=9090)
    health_check_interval: int = Field(default=30)
    
    # Alerts
    alerts_enabled: bool = Field(default=False)
    alert_webhook: Optional[str] = Field(default=None)
    
    # Performance monitoring
    track_processing_time: bool = Field(default=True)
    track_memory_usage: bool = Field(default=True)
    track_api_calls: bool = Field(default=True)


class Config(BaseModel):
    """Main configuration class."""
    
    app: AppConfig = Field(default_factory=AppConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    document_processing: DocumentProcessingConfig = Field(default_factory=DocumentProcessingConfig)
    vector_db: VectorDBConfig = Field(default_factory=VectorDBConfig)
    mcp: MCPConfig = Field(default_factory=MCPConfig)
    cli: CLIConfig = Field(default_factory=CLIConfig)
    query: QueryConfig = Field(default_factory=QueryConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    
    def save(self, path: Path) -> None:
        """Save configuration to YAML file."""
        # Convert to dict and handle Path objects
        config_dict = self.dict()
        
        def convert_paths(obj):
            """Recursively convert Path objects to strings."""
            if isinstance(obj, dict):
                return {k: convert_paths(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_paths(v) for v in obj]
            elif isinstance(obj, Path):
                return str(obj)
            else:
                return obj
        
        config_dict = convert_paths(config_dict)
        
        with open(path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
    
    @classmethod
    def load(cls, path: Path) -> 'Config':
        """Load configuration from YAML file."""
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)


class ConfigManager:
    """Manages application configuration with enhanced features."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file. If None, uses default.
        """
        self.config_path = Path(config_path) if config_path else self._get_default_config_path()
        self.config: Config = self._load_config()
        self._callbacks: List[callable] = []
        
    def _get_default_config_path(self) -> Path:
        """Get default configuration path."""
        # Check environment variable first
        env_path = os.getenv("VECTOR_DB_CONFIG_PATH")
        if env_path:
            return Path(env_path)
            
        # Check multiple default locations
        config_locations = [
            Path.home() / ".vector-db-query" / "config.yaml",
            Path("/etc/vector-db-query/config.yaml"),
            Path(__file__).parent.parent.parent.parent / "config" / "default.yaml",
            Path("./config.yaml"),
        ]
        
        for location in config_locations:
            if location.exists():
                return location
                
        # Use first location as default
        return config_locations[0]
        
    def _load_config(self) -> Config:
        """Load configuration from file and environment."""
        # Load environment variables
        load_dotenv()
        
        # Load YAML config
        config_data = {}
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                config_data = yaml.safe_load(f) or {}
                
        # Apply environment variable overrides
        config_data = self._apply_env_overrides(config_data)
        
        # Create and validate config
        try:
            return Config(**config_data)
        except ValidationError as e:
            raise ValueError(f"Invalid configuration: {e}")
            
    def _apply_env_overrides(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides to configuration."""
        # Enhanced environment variable mappings
        env_mappings = {
            # App settings
            "VECTOR_DB_LOG_LEVEL": ("app", "log_level"),
            "LOG_LEVEL": ("app", "log_level"),
            
            # Paths
            "VECTOR_DB_DATA_DIR": ("paths", "data_dir"),
            "VECTOR_DB_LOG_DIR": ("paths", "log_dir"),
            "VECTOR_DB_CONFIG_DIR": ("paths", "config_dir"),
            
            # Document processing
            "VECTOR_DB_CHUNK_SIZE": ("document_processing", "chunk_size"),
            "VECTOR_DB_CHUNK_OVERLAP": ("document_processing", "chunk_overlap"),
            "VECTOR_DB_CHUNKING_STRATEGY": ("document_processing", "chunking_strategy"),
            "VECTOR_DB_MAX_FILE_SIZE_MB": ("document_processing", "scanner", "max_file_size_mb"),
            
            # OCR settings
            "VECTOR_DB_OCR_ENABLED": ("document_processing", "ocr", "enabled"),
            "VECTOR_DB_OCR_LANGUAGE": ("document_processing", "ocr", "language"),
            "VECTOR_DB_OCR_CONFIDENCE": ("document_processing", "ocr", "confidence_threshold"),
            
            # Format-specific settings
            "VECTOR_DB_EXCEL_EXTRACT_FORMULAS": ("document_processing", "format_settings", "excel", "extract_formulas"),
            "VECTOR_DB_EXCEL_MAX_ROWS": ("document_processing", "format_settings", "excel", "max_rows_per_sheet"),
            "VECTOR_DB_POWERPOINT_EXTRACT_NOTES": ("document_processing", "format_settings", "powerpoint", "extract_speaker_notes"),
            "VECTOR_DB_EMAIL_EXTRACT_ATTACHMENTS": ("document_processing", "format_settings", "email", "extract_attachments"),
            "VECTOR_DB_HTML_CONVERT_MARKDOWN": ("document_processing", "format_settings", "html", "convert_to_markdown"),
            "VECTOR_DB_LOG_SUMMARIZE": ("document_processing", "format_settings", "logs", "summarize"),
            "VECTOR_DB_LOG_MAX_LINES": ("document_processing", "format_settings", "logs", "max_lines"),
            "VECTOR_DB_TEMP_DIR": ("paths", "temp_dir"),
            
            # Embedding
            "VECTOR_DB_EMBEDDING_MODEL": ("embedding", "model"),
            "EMBEDDING_MODEL": ("embedding", "model"),
            "VECTOR_DB_EMBEDDING_DIMENSIONS": ("embedding", "dimensions"),
            "EMBEDDING_DIMENSIONS": ("embedding", "dimensions"),
            "VECTOR_DB_EMBEDDING_TASK_TYPE": ("embedding", "task_type"),
            
            # Vector DB
            "QDRANT_HOST": ("vector_db", "host"),
            "QDRANT_PORT": ("vector_db", "port"),
            "QDRANT_GRPC_PORT": ("vector_db", "grpc_port"),
            "VECTOR_DB_COLLECTION_NAME": ("vector_db", "collection_name"),
            
            # MCP
            "MCP_SERVER_HOST": ("mcp", "server_host"),
            "MCP_SERVER_PORT": ("mcp", "server_port"),
            "MCP_AUTH_ENABLED": ("mcp", "auth_enabled"),
            
            # OCR
            "TESSERACT_CMD": ("document_processing", "ocr", "tesseract_cmd"),
            "OCR_LANGUAGE": ("document_processing", "ocr", "language"),
            "OCR_ENABLED": ("document_processing", "ocr", "enabled"),
            
            # Document Processing
            "CHUNK_SIZE": ("document_processing", "chunk_size"),
            "CHUNK_OVERLAP": ("document_processing", "chunk_overlap"),
            "MAX_FILE_SIZE_MB": ("document_processing", "max_file_size_mb"),
            
            # Monitoring
            "MONITORING_ENABLED": ("monitoring", "enabled"),
            "METRICS_PORT": ("monitoring", "metrics_port"),
        }
        
        for env_var, path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Navigate to the correct nested location
                current = config_data
                for part in path[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                # Convert types as needed
                key = path[-1]
                if key in ["port", "grpc_port", "dimensions", "chunk_size", "chunk_overlap", 
                          "max_file_size_mb", "metrics_port", "server_port", "max_rows_per_sheet",
                          "max_lines", "dpi", "health_check_interval", "max_workers"]:
                    try:
                        value = int(value)
                    except ValueError:
                        continue
                elif key in ["enabled", "auth_enabled", "extract_metadata", "parallel_processing",
                            "extract_formulas", "extract_comments", "process_all_sheets", 
                            "extract_speaker_notes", "extract_slide_numbers", "include_master_slides",
                            "extract_attachments", "thread_detection", "sanitize_content",
                            "include_headers", "remove_scripts", "remove_styles", "convert_to_markdown",
                            "preserve_links", "preserve_structure", "include_comments", "validate_syntax",
                            "summarize", "extract_patterns", "preprocess_image"]:
                    value = value.lower() in ["true", "1", "yes", "on"]
                elif key in ["confidence_threshold", "score_threshold", "keyword_weight", "max_file_size_mb"]:
                    try:
                        value = float(value)
                    except ValueError:
                        continue
                        
                current[key] = value
                
        return config_data
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key."""
        parts = key.split(".")
        value = self.config.dict()
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
                
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by dot-notation key."""
        parts = key.split(".")
        config_dict = self.config.dict()
        current = config_dict
        
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
            
        current[parts[-1]] = value
        
        # Recreate config to validate
        self.config = Config(**config_dict)
        
        # Notify callbacks
        for callback in self._callbacks:
            callback(key, value)
    
    def subscribe(self, callback: callable) -> None:
        """Subscribe to configuration changes."""
        self._callbacks.append(callback)
    
    def unsubscribe(self, callback: callable) -> None:
        """Unsubscribe from configuration changes."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
        
    def reload(self) -> None:
        """Reload configuration from file."""
        old_config = self.config
        self.config = self._load_config()
        
        # Notify callbacks of changes
        old_dict = old_config.dict()
        new_dict = self.config.dict()
        
        def find_changes(old, new, path=""):
            for key in set(old.keys()) | set(new.keys()):
                current_path = f"{path}.{key}" if path else key
                if key not in old:
                    for callback in self._callbacks:
                        callback(current_path, new[key])
                elif key not in new:
                    for callback in self._callbacks:
                        callback(current_path, None)
                elif old[key] != new[key]:
                    if isinstance(old[key], dict) and isinstance(new[key], dict):
                        find_changes(old[key], new[key], current_path)
                    else:
                        for callback in self._callbacks:
                            callback(current_path, new[key])
                            
        find_changes(old_dict, new_dict)
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []
        
        # Check paths exist
        for path_field in ["data_dir", "log_dir", "config_dir"]:
            path = getattr(self.config.paths, path_field)
            if not path.exists():
                issues.append(f"Path {path_field} does not exist: {path}")
                
        # Check file size limits
        if self.config.document_processing.max_file_size_mb <= 0:
            issues.append("max_file_size_mb must be positive")
            
        # Check chunk settings
        if self.config.document_processing.chunk_size <= 0:
            issues.append("chunk_size must be positive")
        if self.config.document_processing.chunk_overlap >= self.config.document_processing.chunk_size:
            issues.append("chunk_overlap must be less than chunk_size")
            
        # Check OCR settings
        if self.config.document_processing.ocr.enabled:
            if self.config.document_processing.ocr.tesseract_cmd:
                if not Path(self.config.document_processing.ocr.tesseract_cmd).exists():
                    issues.append(f"Tesseract command not found: {self.config.document_processing.ocr.tesseract_cmd}")
                    
        # Check vector size consistency
        if self.config.embedding.dimensions != self.config.vector_db.vector_size:
            issues.append("Embedding dimensions must match vector_db vector_size")
            
        return issues
    
    def export_env(self) -> Dict[str, str]:
        """Export configuration as environment variables."""
        env_vars = {}
        
        # Flatten configuration to environment variables
        def flatten(obj, prefix="VECTOR_DB"):
            if isinstance(obj, BaseModel):
                obj = obj.dict()
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_prefix = f"{prefix}_{key.upper()}"
                    flatten(value, new_prefix)
            elif isinstance(obj, (list, set)):
                env_vars[prefix] = ",".join(str(v) for v in obj)
            elif isinstance(obj, Path):
                env_vars[prefix] = str(obj)
            elif obj is not None:
                env_vars[prefix] = str(obj)
                
        flatten(self.config)
        return env_vars


# Global configuration instance
_config_manager: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def reload_config() -> None:
    """Reload global configuration."""
    global _config_manager
    if _config_manager is not None:
        _config_manager.reload()


def reset_config() -> None:
    """Reset global configuration instance."""
    global _config_manager
    _config_manager = None