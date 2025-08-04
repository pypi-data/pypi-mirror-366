# Changelog

All notable changes to Vector DB Query will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-08-03

### 🎉 First Production Release

This is the first production release of Vector DB Query, a powerful CLI application for vector database queries using LLMs via MCP.

### Added

#### Core Features
- **Vector Database Integration** - Full Qdrant support with collection management
- **LLM Integration** - Google Generative AI embeddings and query capabilities
- **MCP Server** - Model Context Protocol server for LLM integration
- **Document Processing** - Support for 40+ file formats including:
  - Documents: PDF, Word, ODT, RTF, Markdown
  - Spreadsheets: Excel, CSV, ODS
  - Presentations: PowerPoint, ODP
  - Email: EML, MBOX
  - Web: HTML, XML
  - Images: OCR support for PNG, JPG, GIF, BMP, TIFF
  - Archives: ZIP, TAR, 7Z
  - Data: JSON, YAML, TOML, INI

#### Data Source Integration
- **Gmail Integration** - OAuth2 authentication, IMAP connectivity, email processing
- **Fireflies.ai Integration** - Webhook endpoint, API client, transcript processing  
- **Google Drive Integration** - OAuth2 flow, Gemini transcript detection
- **Content Deduplication** - Hash-based and similarity-based deduplication
- **NLP Processing** - Entity extraction and sentiment analysis with spaCy
- **Setup Wizard** - Interactive configuration for easy onboarding

#### Monitoring & Management
- **Enterprise Monitoring Dashboard** - Real-time metrics and controls
- **Service Management** - Start, stop, restart services with PM2 integration
- **Connection Monitoring** - Track Qdrant, MCP, database connections
- **Performance Tracking** - Query performance metrics and optimization
- **Notification System** - Email, push, toast notifications
- **Audit Logging** - Comprehensive activity tracking

#### Developer Experience
- **CLI Interface** - Rich command-line interface with 50+ commands
- **Configuration Management** - YAML config with environment overrides
- **Export Capabilities** - PDF, CSV, JSON, Excel, HTML exports
- **API Key Management** - Secure API key generation and management
- **Widget Library** - Customizable dashboard widgets
- **Comprehensive Testing** - 135+ tests with full coverage

### Infrastructure
- **Docker Support** - Production-ready Docker configurations
- **Kubernetes Support** - K8s manifests for scalable deployment
- **Database Support** - SQLite and PostgreSQL
- **Caching** - Redis integration for performance
- **Monitoring** - Prometheus and Grafana integration

### Documentation
- Complete user documentation
- API reference
- Deployment guides
- Troubleshooting guides
- Example configurations

## [Unreleased]

### Added
- Future enhancements will be tracked here

## Previous Versions

Note: This is the first public release. Previous version numbers were used during development.

### 🎉 Major Release: Enhanced File Format Support

This release brings comprehensive file format support, advanced configuration management, and improved CLI features.

### Added

#### 📄 File Format Support (39+ formats)
- **Document Formats**
  - PDF reader with table extraction and metadata support
  - Microsoft Word (.doc, .docx) with formatting preservation
  - OpenDocument formats (.odt, .ods, .odp)
  - Rich Text Format (.rtf)
  - Enhanced Markdown parsing with code block detection

- **Spreadsheet Support**
  - Excel reader (.xlsx, .xls) with multi-sheet processing
  - CSV reader with automatic delimiter detection
  - Table structure preservation
  - Formula results extraction

- **Presentation Support**
  - PowerPoint reader (.pptx, .ppt)
  - Slide text and speaker notes extraction
  - Layout preservation

- **Email Support**
  - EML file reader with header extraction
  - MBOX archive support with thread reconstruction
  - Attachment listing

- **Web & Markup**
  - HTML reader with clean text extraction
  - XML reader with structure preservation
  - Metadata extraction (title, description, keywords)

- **Configuration Files**
  - JSON reader with pretty printing
  - YAML reader with multi-document support
  - XML reader with attribute handling
  - INI/Config reader (.ini, .cfg, .conf, .config)
  - TOML support

- **Image OCR**
  - Support for PNG, JPG, JPEG, GIF, BMP, TIFF, WebP
  - Multi-page TIFF support
  - Configurable OCR languages
  - Confidence threshold filtering
  - Image preprocessing for better accuracy
  - Tesseract integration

- **Archive Support**
  - ZIP file extraction and processing
  - TAR archive support (.tar, .tar.gz, .tar.bz2, .tar.xz)
  - 7-Zip support
  - Nested archive handling
  - Password-protected archive support

- **Data Formats**
  - GeoJSON support with structure preservation
  - JSON Lines (.jsonl, .ndjson) streaming
  - Log file analysis with level detection

#### ⚙️ Configuration System Enhancements
- Comprehensive configuration management with `ConfigManager`
- YAML-based configuration with environment variable overrides
- Configuration validation and health checks
- Change notification system with callbacks
- Multiple configuration profiles support
- CLI commands for configuration management:
  - `config show` - Display configuration in multiple formats
  - `config get/set` - Manage individual settings
  - `config validate` - Check configuration health
  - `config formats` - View supported file formats
  - `config add-format` - Add custom extensions
  - `config export/load` - Save and load configurations
  - `config env` - Show environment variable mappings

#### 🎨 CLI Enhancements
- **Enhanced Process Command**
  - `--formats` flag to display all supported formats
  - `--extensions` option for format filtering
  - `--exclude` option to exclude specific formats
  - `--ocr-lang` option for OCR language selection
  - `--ocr-confidence` option for confidence threshold
  - `--no-ocr` flag to disable OCR
  - `--stats` flag for detailed processing statistics
  - Format-aware progress reporting

- **New Commands**
  - `detect-format` - Detect file format support
  - `config` command group for configuration management

#### 🔧 Technical Improvements
- Modular reader architecture with base classes
- Factory pattern for reader selection
- Consistent error handling across all readers
- Metadata extraction for all file types
- Memory-efficient streaming for large files
- Parallel processing support
- Progress callbacks for all operations

#### 📊 Other Enhancements
- Interactive CLI with rich terminal interface
- MCP server for AI assistant integration
- Comprehensive test suite with 80%+ coverage
- Docker and Kubernetes deployment support
- CI/CD pipeline with GitHub Actions
- Monitoring dashboard with Streamlit
- PM2 process management integration
- Real-time system metrics collection

### Changed
- Upgraded configuration system to support all new features
- Enhanced document processor to handle 39+ file formats
- Improved error messages with format-specific guidance
- Updated progress reporting to show format breakdown
- Refactored reader system for better extensibility
- Improved document processing performance
- Enhanced error messages with helpful suggestions
- Updated documentation with comprehensive guides

### Fixed
- HTML reader spacing issues between inline elements
- XML attribute extraction in nested elements
- INI file interpolation errors
- Log reader level counting accuracy
- Configuration path resolution on different platforms
- Memory leak in batch processing
- Connection timeout issues with Qdrant
- PDF extraction for encrypted files

### Performance
- Optimized batch processing for multiple file formats
- Added streaming support for large files
- Implemented connection pooling for database operations
- Enhanced memory management for OCR operations

### Documentation
- Comprehensive file formats guide
- Updated configuration guide
- Enhanced CLI features documentation
- Complete API reference
- Migration guide from 1.x to 2.0

## [1.0.0] - 2024-01-28

### Added
- Initial release
- Document processing for PDF, Word, Markdown, and text files
- Vector storage using Qdrant
- Semantic search with natural language queries
- Interactive CLI with menu system
- File browser with preview
- Query builder with history
- Configuration management
- MCP server implementation
- Batch processing support
- Multiple embedding providers (Google, OpenAI)
- Export functionality
- Performance monitoring
- Usage analytics

### Security
- Secure API key storage
- MCP authentication
- Input validation

## [0.9.0-beta] - 2024-01-15

### Added
- Beta release for testing
- Core functionality implementation
- Basic CLI interface
- Qdrant integration
- Document processing pipeline

### Known Issues
- Limited file format support
- No interactive mode
- Basic error handling

[Unreleased]: https://github.com/your-org/vector-db-query/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/your-org/vector-db-query/compare/v0.9.0-beta...v1.0.0
[0.9.0-beta]: https://github.com/your-org/vector-db-query/releases/tag/v0.9.0-beta