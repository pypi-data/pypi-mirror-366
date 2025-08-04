"""Configuration and structured data file readers."""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml
import configparser
import re
from datetime import datetime

from vector_db_query.document_processor.base import DocumentReader
from vector_db_query.document_processor.exceptions import DocumentReadError
from vector_db_query.utils.logger import get_logger

logger = get_logger(__name__)


class ConfigReader(DocumentReader):
    """Base reader for configuration and structured data files."""
    
    def __init__(self, pretty_print: bool = True, preserve_structure: bool = True):
        """Initialize config reader.
        
        Args:
            pretty_print: Whether to format output nicely
            preserve_structure: Whether to preserve hierarchical structure
        """
        super().__init__()
        self.pretty_print = pretty_print
        self.preserve_structure = preserve_structure
        self._metadata = {}
        
    def can_read(self, file_path: Path) -> bool:
        """Check if this reader can handle the file type."""
        return file_path.suffix.lower() in self.supported_extensions
        
    @property
    def supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        return []  # Override in subclasses
        
    def supports_extension(self, extension: str) -> bool:
        """Check if a file extension is supported.
        
        Args:
            extension: File extension (with or without dot)
            
        Returns:
            True if the extension is supported
        """
        if not extension:
            return False
            
        # Normalize extension
        if not extension.startswith('.'):
            extension = f'.{extension}'
            
        return extension.lower() in self.supported_extensions


class JSONReader(ConfigReader):
    """Reader for JSON files."""
    
    def read(self, file_path: Path) -> str:
        """Read JSON file and convert to formatted text."""
        if isinstance(file_path, str):
            file_path = Path(file_path)
            
        logger.info(f"Reading JSON file: {file_path.name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Extract metadata
            self._metadata = {
                'file_name': file_path.name,
                'file_size': file_path.stat().st_size,
                'type': 'json',
                'key_count': self._count_keys(data) if isinstance(data, dict) else 0,
                'array_length': len(data) if isinstance(data, list) else 0
            }
            
            # Convert to text
            if self.pretty_print:
                return json.dumps(data, indent=2, ensure_ascii=False)
            else:
                return json.dumps(data, ensure_ascii=False)
                
        except json.JSONDecodeError as e:
            raise DocumentReadError(
                f"Invalid JSON file: {e}",
                file_path=str(file_path)
            )
        except Exception as e:
            raise DocumentReadError(
                f"Failed to read JSON file: {e}",
                file_path=str(file_path)
            )
            
    @property
    def supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        return ['.json', '.jsonl', '.geojson']
        
    def _count_keys(self, obj: Any, count: int = 0) -> int:
        """Recursively count keys in a JSON object."""
        if isinstance(obj, dict):
            count += len(obj)
            for value in obj.values():
                count = self._count_keys(value, count)
        elif isinstance(obj, list):
            for item in obj:
                count = self._count_keys(item, count)
        return count


class XMLReader(ConfigReader):
    """Reader for XML files."""
    
    def read(self, file_path: Path) -> str:
        """Read XML file and convert to formatted text."""
        if isinstance(file_path, str):
            file_path = Path(file_path)
            
        logger.info(f"Reading XML file: {file_path.name}")
        
        try:
            tree = ET.parse(str(file_path))
            root = tree.getroot()
            
            # Extract metadata
            self._metadata = {
                'file_name': file_path.name,
                'file_size': file_path.stat().st_size,
                'type': 'xml',
                'root_tag': root.tag,
                'element_count': len(root.findall('.//')),
                'namespace': root.tag.split('}')[0][1:] if '}' in root.tag else None
            }
            
            # Convert to text
            if self.preserve_structure:
                return self._xml_to_text(root)
            else:
                # Just extract all text content
                return ' '.join(root.itertext()).strip()
                
        except ET.ParseError as e:
            raise DocumentReadError(
                f"Invalid XML file: {e}",
                file_path=str(file_path)
            )
        except Exception as e:
            raise DocumentReadError(
                f"Failed to read XML file: {e}",
                file_path=str(file_path)
            )
            
    @property
    def supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        return ['.xml', '.xsd', '.xsl', '.svg']
        
    def _xml_to_text(self, element: ET.Element, indent: int = 0) -> str:
        """Convert XML element to indented text representation."""
        lines = []
        indent_str = '  ' * indent
        
        # Element with text only and attributes
        if element.text and element.text.strip() and not list(element):
            lines.append(f"{indent_str}{element.tag}: {element.text.strip()}")
            # Add attributes after the element if it has text
            if element.attrib:
                for key, value in element.attrib.items():
                    lines.append(f"{indent_str}  @{key}: {value}")
            
        # Element with children or no text
        else:
            lines.append(f"{indent_str}{element.tag}:")
            
            # Add attributes first
            if element.attrib:
                for key, value in element.attrib.items():
                    lines.append(f"{indent_str}  @{key}: {value}")
                    
            # Then add text if any
            if element.text and element.text.strip():
                lines.append(f"{indent_str}  {element.text.strip()}")
                    
            # Process children
            for child in element:
                lines.append(self._xml_to_text(child, indent + 1))
                
        return '\n'.join(lines)


class YAMLReader(ConfigReader):
    """Reader for YAML files."""
    
    def read(self, file_path: Path) -> str:
        """Read YAML file and convert to formatted text."""
        if isinstance(file_path, str):
            file_path = Path(file_path)
            
        logger.info(f"Reading YAML file: {file_path.name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Load all documents in the file
                documents = list(yaml.safe_load_all(f))
                
            # Extract metadata
            self._metadata = {
                'file_name': file_path.name,
                'file_size': file_path.stat().st_size,
                'type': 'yaml',
                'document_count': len(documents),
                'key_count': self._count_yaml_keys(documents)
            }
            
            # Convert to text
            if len(documents) == 1:
                # Single document
                if self.pretty_print:
                    return yaml.dump(documents[0], default_flow_style=False, allow_unicode=True)
                else:
                    return str(documents[0])
            else:
                # Multiple documents
                output = []
                for i, doc in enumerate(documents):
                    if i > 0:
                        output.append('---')
                    if self.pretty_print:
                        output.append(yaml.dump(doc, default_flow_style=False, allow_unicode=True))
                    else:
                        output.append(str(doc))
                return '\n'.join(output)
                
        except yaml.YAMLError as e:
            raise DocumentReadError(
                f"Invalid YAML file: {e}",
                file_path=str(file_path)
            )
        except Exception as e:
            raise DocumentReadError(
                f"Failed to read YAML file: {e}",
                file_path=str(file_path)
            )
            
    @property
    def supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        return ['.yaml', '.yml']
        
    def _count_yaml_keys(self, documents: List[Any]) -> int:
        """Count total keys in YAML documents."""
        count = 0
        for doc in documents:
            if isinstance(doc, dict):
                count += self._count_keys(doc)
        return count
        
    def _count_keys(self, obj: Any, count: int = 0) -> int:
        """Recursively count keys in a YAML object."""
        if isinstance(obj, dict):
            count += len(obj)
            for value in obj.values():
                count = self._count_keys(value, count)
        elif isinstance(obj, list):
            for item in obj:
                count = self._count_keys(item, count)
        return count


class INIReader(ConfigReader):
    """Reader for INI/CFG configuration files."""
    
    def read(self, file_path: Path) -> str:
        """Read INI file and convert to formatted text."""
        if isinstance(file_path, str):
            file_path = Path(file_path)
            
        logger.info(f"Reading INI/CFG file: {file_path.name}")
        
        try:
            # Use RawConfigParser to avoid interpolation issues
            config = configparser.RawConfigParser()
            config.read(str(file_path))
            
            # Extract metadata
            self._metadata = {
                'file_name': file_path.name,
                'file_size': file_path.stat().st_size,
                'type': 'ini',
                'section_count': len(config.sections()),
                'total_keys': sum(len(config[section]) for section in config.sections())
            }
            
            # Convert to text
            lines = []
            
            # Add default section if it has values
            if config.defaults():
                lines.append("[DEFAULT]")
                for key, value in config.defaults().items():
                    lines.append(f"{key} = {value}")
                lines.append("")
                
            # Add other sections
            for section in config.sections():
                lines.append(f"[{section}]")
                for key, value in config[section].items():
                    lines.append(f"{key} = {value}")
                lines.append("")
                
            return '\n'.join(lines).strip()
            
        except configparser.Error as e:
            raise DocumentReadError(
                f"Invalid INI/CFG file: {e}",
                file_path=str(file_path)
            )
        except Exception as e:
            raise DocumentReadError(
                f"Failed to read INI/CFG file: {e}",
                file_path=str(file_path)
            )
            
    @property
    def supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        return ['.ini', '.cfg', '.conf', '.config']


class LogReader(ConfigReader):
    """Reader for log files with structure parsing."""
    
    def __init__(self, extract_timestamps: bool = True, 
                 extract_levels: bool = True,
                 summarize: bool = False):
        """Initialize log reader.
        
        Args:
            extract_timestamps: Whether to extract timestamps
            extract_levels: Whether to extract log levels
            summarize: Whether to provide a summary instead of full content
        """
        super().__init__()
        self.extract_timestamps = extract_timestamps
        self.extract_levels = extract_levels
        self.summarize = summarize
        
        # Common log level patterns
        self.level_pattern = re.compile(
            r'\b(DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL|FATAL|TRACE)\b',
            re.IGNORECASE
        )
        
        # Common timestamp patterns
        self.timestamp_patterns = [
            # ISO format: 2024-01-15T10:30:45
            re.compile(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}'),
            # Log format: [2024-01-15 10:30:45]
            re.compile(r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]'),
            # Syslog format: Jan 15 10:30:45
            re.compile(r'[A-Za-z]{3} \d{1,2} \d{2}:\d{2}:\d{2}'),
        ]
        
    def read(self, file_path: Path) -> str:
        """Read log file and extract structured information."""
        if isinstance(file_path, str):
            file_path = Path(file_path)
            
        logger.info(f"Reading log file: {file_path.name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
                
            # Analyze log structure
            log_stats = self._analyze_log(lines)
            
            # Extract metadata
            self._metadata = {
                'file_name': file_path.name,
                'file_size': file_path.stat().st_size,
                'type': 'log',
                'line_count': len(lines),
                'error_count': log_stats.get('ERROR', 0),
                'warning_count': log_stats.get('WARNING', 0) + log_stats.get('WARN', 0),
                'info_count': log_stats.get('INFO', 0),
                'debug_count': log_stats.get('DEBUG', 0) + log_stats.get('TRACE', 0),
                'timestamp_range': log_stats.get('timestamp_range', 'Unknown')
            }
            
            # Return content based on mode
            if self.summarize:
                return self._create_summary(lines, log_stats)
            else:
                # Return full content with optional structure markers
                if self.preserve_structure:
                    return self._add_structure_markers(lines)
                else:
                    return ''.join(lines)
                    
        except Exception as e:
            raise DocumentReadError(
                f"Failed to read log file: {e}",
                file_path=str(file_path)
            )
            
    @property
    def supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        return ['.log', '.txt']  # .txt files that look like logs
        
    def _analyze_log(self, lines: List[str]) -> Dict[str, Any]:
        """Analyze log file structure and statistics."""
        stats = {}
        timestamps = []
        
        for line in lines:
            # Extract log levels
            if self.extract_levels:
                match = self.level_pattern.search(line)
                if match:
                    level = match.group(1).upper()
                    stats[level] = stats.get(level, 0) + 1
                    
            # Extract timestamps
            if self.extract_timestamps:
                for pattern in self.timestamp_patterns:
                    match = pattern.search(line)
                    if match:
                        timestamps.append(match.group(0))
                        break
                        
        # Determine timestamp range
        if timestamps:
            stats['timestamp_range'] = f"{timestamps[0]} to {timestamps[-1]}"
            
        return stats
        
    def _create_summary(self, lines: List[str], stats: Dict[str, Any]) -> str:
        """Create a summary of the log file."""
        summary = [
            f"Log File Summary",
            f"=" * 50,
            f"Total Lines: {len(lines)}",
            f"",
            f"Log Levels:",
        ]
        
        for level in ['DEBUG', 'INFO', 'WARNING', 'WARN', 'ERROR', 'CRITICAL', 'FATAL']:
            if level in stats:
                summary.append(f"  {level}: {stats[level]}")
                
        summary.extend([
            f"",
            f"Timestamp Range: {stats.get('timestamp_range', 'Unknown')}",
            f"",
            f"Recent Errors (last 5):",
        ])
        
        # Extract recent errors
        error_lines = []
        for i, line in enumerate(reversed(lines)):
            if 'ERROR' in line.upper() and len(error_lines) < 5:
                error_lines.append(f"  Line {len(lines)-i}: {line.strip()[:100]}...")
                
        summary.extend(error_lines or ["  No errors found"])
        
        return '\n'.join(summary)
        
    def _add_structure_markers(self, lines: List[str]) -> str:
        """Add structure markers to log lines."""
        structured_lines = []
        
        for line in lines:
            # Mark errors
            if 'ERROR' in line.upper() or 'CRITICAL' in line.upper():
                structured_lines.append(f"[ERROR] {line}")
            elif 'WARNING' in line.upper() or 'WARN' in line.upper():
                structured_lines.append(f"[WARN] {line}")
            else:
                structured_lines.append(line)
                
        return ''.join(structured_lines)


# Update the reader factory to include config readers
def register_config_readers(factory):
    """Register all config readers with the factory.
    
    Args:
        factory: ReaderFactory instance to register with
    """
    factory.register_reader('json', JSONReader())
    factory.register_reader('xml', XMLReader())
    factory.register_reader('yaml', YAMLReader())
    factory.register_reader('ini', INIReader())
    factory.register_reader('log', LogReader())