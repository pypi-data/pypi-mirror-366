#!/usr/bin/env python3
"""Create sample configuration files for testing."""

import json
import yaml
import xml.etree.ElementTree as ET
from pathlib import Path
import configparser


def create_json_samples():
    """Create sample JSON files."""
    
    # Simple JSON object
    simple_data = {
        "app_name": "Vector DB Query",
        "version": "1.0.0",
        "settings": {
            "debug": True,
            "port": 8080,
            "host": "localhost"
        },
        "features": ["search", "index", "query", "export"],
        "database": {
            "type": "qdrant",
            "url": "http://localhost:6333",
            "collection": "documents"
        }
    }
    
    with open('config.json', 'w') as f:
        json.dump(simple_data, f, indent=2)
    print("Created: config.json")
    
    # Package.json style
    package_data = {
        "name": "vector-db-query",
        "version": "0.1.0",
        "description": "Query vector databases with natural language",
        "main": "src/index.py",
        "scripts": {
            "start": "python -m vector_db_query",
            "test": "pytest tests/",
            "lint": "flake8 src/"
        },
        "dependencies": {
            "qdrant-client": "^1.7.0",
            "langchain": "^0.1.0",
            "openai": "^1.0.0"
        },
        "devDependencies": {
            "pytest": "^7.0.0",
            "flake8": "^6.0.0"
        }
    }
    
    with open('package.json', 'w') as f:
        json.dump(package_data, f, indent=2)
    print("Created: package.json")
    
    # Data array
    data_array = [
        {"id": 1, "name": "Document 1", "type": "pdf", "size": 1024},
        {"id": 2, "name": "Document 2", "type": "docx", "size": 2048},
        {"id": 3, "name": "Document 3", "type": "txt", "size": 512}
    ]
    
    with open('data.json', 'w') as f:
        json.dump(data_array, f, indent=2)
    print("Created: data.json")


def create_xml_samples():
    """Create sample XML files."""
    
    # Configuration XML
    root = ET.Element("configuration")
    
    app = ET.SubElement(root, "application")
    ET.SubElement(app, "name").text = "Vector DB Query"
    ET.SubElement(app, "version").text = "1.0.0"
    ET.SubElement(app, "author").text = "AI Assistant"
    
    database = ET.SubElement(root, "database")
    database.set("type", "vector")
    ET.SubElement(database, "host").text = "localhost"
    ET.SubElement(database, "port").text = "6333"
    ET.SubElement(database, "collection").text = "documents"
    
    features = ET.SubElement(root, "features")
    for feature_name in ["search", "index", "query", "export"]:
        feature = ET.SubElement(features, "feature")
        feature.set("enabled", "true")
        feature.text = feature_name
    
    tree = ET.ElementTree(root)
    tree.write("config.xml", encoding="UTF-8", xml_declaration=True)
    print("Created: config.xml")
    
    # SVG sample
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
    <rect x="10" y="10" width="80" height="80" fill="blue"/>
    <circle cx="50" cy="50" r="30" fill="yellow"/>
    <text x="50" y="55" text-anchor="middle" fill="black">VDB</text>
</svg>'''
    
    with open('logo.svg', 'w') as f:
        f.write(svg_content)
    print("Created: logo.svg")


def create_yaml_samples():
    """Create sample YAML files."""
    
    # Application config
    app_config = {
        'application': {
            'name': 'Vector DB Query',
            'version': '1.0.0',
            'environment': 'development'
        },
        'server': {
            'host': 'localhost',
            'port': 8080,
            'workers': 4,
            'timeout': 30
        },
        'database': {
            'provider': 'qdrant',
            'connection': {
                'host': 'localhost',
                'port': 6333,
                'secure': False
            },
            'collections': ['documents', 'embeddings']
        },
        'features': {
            'search': {
                'enabled': True,
                'max_results': 10,
                'similarity_threshold': 0.7
            },
            'indexing': {
                'enabled': True,
                'batch_size': 100,
                'embedding_model': 'text-embedding-ada-002'
            }
        }
    }
    
    with open('config.yaml', 'w') as f:
        yaml.dump(app_config, f, default_flow_style=False)
    print("Created: config.yaml")
    
    # Docker compose style
    compose_data = {
        'version': '3.8',
        'services': {
            'qdrant': {
                'image': 'qdrant/qdrant:latest',
                'ports': ['6333:6333'],
                'volumes': ['./qdrant_storage:/qdrant/storage']
            },
            'app': {
                'build': '.',
                'depends_on': ['qdrant'],
                'environment': {
                    'QDRANT_URL': 'http://qdrant:6333',
                    'LOG_LEVEL': 'INFO'
                },
                'ports': ['8080:8080']
            }
        },
        'volumes': {
            'qdrant_storage': None
        }
    }
    
    with open('docker-compose.yml', 'w') as f:
        yaml.dump(compose_data, f, default_flow_style=False)
    print("Created: docker-compose.yml")


def create_ini_samples():
    """Create sample INI/CFG files."""
    
    # Standard INI
    config = configparser.ConfigParser()
    
    config['DEFAULT'] = {
        'ServerAliveInterval': '45',
        'Compression': 'yes',
        'CompressionLevel': '9'
    }
    
    config['database'] = {
        'host': 'localhost',
        'port': '6333',
        'name': 'vector_db',
        'collection': 'documents'
    }
    
    config['application'] = {
        'name': 'Vector DB Query',
        'version': '1.0.0',
        'debug': 'true',
        'log_level': 'INFO'
    }
    
    config['paths'] = {
        'data': './data',
        'logs': './logs',
        'cache': './cache',
        'uploads': './uploads'
    }
    
    with open('settings.ini', 'w') as f:
        config.write(f)
    print("Created: settings.ini")
    
    # Git-style config
    git_config = """[core]
    repositoryformatversion = 0
    filemode = true
    bare = false
    logallrefupdates = true

[remote "origin"]
    url = https://github.com/example/vector-db-query.git
    fetch = +refs/heads/*:refs/remotes/origin/*

[branch "main"]
    remote = origin
    merge = refs/heads/main

[user]
    name = AI Assistant
    email = ai@example.com
"""
    
    with open('git.config', 'w') as f:
        f.write(git_config)
    print("Created: git.config")


def create_log_samples():
    """Create sample log files."""
    
    # Application log
    app_log = """[2025-01-30 09:00:00] INFO Application starting...
[2025-01-30 09:00:01] INFO Loading configuration from config.yaml
[2025-01-30 09:00:02] DEBUG Configuration loaded: {'host': 'localhost', 'port': 8080}
[2025-01-30 09:00:03] INFO Connecting to Qdrant at localhost:6333
[2025-01-30 09:00:04] INFO Successfully connected to vector database
[2025-01-30 09:00:05] INFO Loading embedding model: text-embedding-ada-002
[2025-01-30 09:00:10] WARNING Model loading took longer than expected (5.2s)
[2025-01-30 09:00:11] INFO Server started on http://localhost:8080
[2025-01-30 09:15:32] INFO Processing query: "find similar documents"
[2025-01-30 09:15:33] DEBUG Query embedding generated in 0.8s
[2025-01-30 09:15:34] INFO Found 5 similar documents
[2025-01-30 09:15:35] ERROR Failed to retrieve document id=123: Document not found
[2025-01-30 09:15:36] INFO Returning 4 results to client
[2025-01-30 09:30:00] INFO Health check passed
[2025-01-30 09:45:00] INFO Health check passed
[2025-01-30 10:00:00] WARNING High memory usage detected: 85%
[2025-01-30 10:00:01] INFO Running garbage collection
[2025-01-30 10:00:05] INFO Memory usage reduced to 65%
[2025-01-30 11:00:00] CRITICAL Database connection lost
[2025-01-30 11:00:01] ERROR Failed to reconnect: Connection refused
[2025-01-30 11:00:05] INFO Attempting reconnection (attempt 2/5)
[2025-01-30 11:00:10] INFO Successfully reconnected to database
[2025-01-30 11:00:11] INFO Service recovery complete
"""
    
    with open('application.log', 'w') as f:
        f.write(app_log)
    print("Created: application.log")
    
    # Access log
    access_log = """127.0.0.1 - - [30/Jan/2025:09:15:32 +0000] "POST /api/search HTTP/1.1" 200 1543 "-" "Mozilla/5.0"
127.0.0.1 - - [30/Jan/2025:09:16:45 +0000] "GET /api/health HTTP/1.1" 200 52 "-" "curl/7.68.0"
192.168.1.100 - - [30/Jan/2025:09:18:22 +0000] "POST /api/index HTTP/1.1" 201 128 "-" "Python/3.9 aiohttp/3.8.1"
127.0.0.1 - - [30/Jan/2025:09:20:15 +0000] "GET /api/collections HTTP/1.1" 200 256 "-" "Mozilla/5.0"
192.168.1.101 - - [30/Jan/2025:09:22:33 +0000] "DELETE /api/documents/123 HTTP/1.1" 404 68 "-" "curl/7.68.0"
127.0.0.1 - - [30/Jan/2025:09:25:41 +0000] "POST /api/search HTTP/1.1" 500 95 "-" "Mozilla/5.0"
192.168.1.100 - - [30/Jan/2025:09:30:00 +0000] "GET /api/health HTTP/1.1" 200 52 "-" "monitoring-agent/1.0"
"""
    
    with open('access.log', 'w') as f:
        f.write(access_log)
    print("Created: access.log")


def main():
    """Create all sample configuration files."""
    print("Creating sample configuration files...")
    
    # Change to the config directory
    config_dir = Path(__file__).parent
    original_dir = Path.cwd()
    
    try:
        import os
        os.chdir(config_dir)
        
        create_json_samples()
        create_xml_samples()
        create_yaml_samples()
        create_ini_samples()
        create_log_samples()
        
        print("\nAll sample configuration files created successfully!")
        print(f"Files created in: {config_dir}")
        
    finally:
        os.chdir(original_dir)


if __name__ == '__main__':
    main()