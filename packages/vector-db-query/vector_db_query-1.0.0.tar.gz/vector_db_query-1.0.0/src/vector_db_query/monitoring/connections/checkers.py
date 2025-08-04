"""
Connection checkers for various connection types.
"""

import asyncio
import time
import logging
from datetime import datetime
from typing import Dict, Optional, Any, List
from abc import ABC, abstractmethod
import aiohttp
import socket
import subprocess
import json

from .models import (
    Connection, ConnectionCheck, ConnectionStatus, 
    ConnectionHealth, ConnectionType
)

logger = logging.getLogger(__name__)


class ConnectionChecker(ABC):
    """Abstract base class for connection checkers."""
    
    @abstractmethod
    async def check(self, connection: Connection) -> ConnectionCheck:
        """
        Check the connection status.
        
        Args:
            connection: Connection to check
            
        Returns:
            ConnectionCheck result
        """
        pass
    
    def determine_health(self, connection: Connection, check: ConnectionCheck) -> ConnectionHealth:
        """
        Determine connection health based on check result and metrics.
        
        Args:
            connection: Connection being checked
            check: Check result
            
        Returns:
            ConnectionHealth status
        """
        if not check.success:
            if connection.consecutive_failures >= 5:
                return ConnectionHealth.CRITICAL
            elif connection.consecutive_failures >= 3:
                return ConnectionHealth.UNHEALTHY
            else:
                return ConnectionHealth.DEGRADED
        
        # Check based on metrics
        metrics = connection.metrics
        
        # Latency-based health
        if metrics.latency_ms > 1000:
            return ConnectionHealth.DEGRADED
        elif metrics.latency_ms > 2000:
            return ConnectionHealth.UNHEALTHY
        
        # Error rate-based health
        if metrics.error_rate > 0.1:  # 10% error rate
            return ConnectionHealth.DEGRADED
        elif metrics.error_rate > 0.25:  # 25% error rate
            return ConnectionHealth.UNHEALTHY
        
        return ConnectionHealth.HEALTHY


class QdrantChecker(ConnectionChecker):
    """Checker for Qdrant vector database connections."""
    
    async def check(self, connection: Connection) -> ConnectionCheck:
        """Check Qdrant connection."""
        start_time = time.time()
        check = ConnectionCheck(connection_id=connection.id)
        
        try:
            # Import Qdrant client
            from qdrant_client import QdrantClient
            from qdrant_client.http.exceptions import UnexpectedResponse
            
            # Create client
            client = QdrantClient(
                host=connection.host or "localhost",
                port=connection.port or 6333,
                timeout=connection.timeout_seconds
            )
            
            # Try to get collections (health check)
            collections = client.get_collections()
            
            # Success
            check.success = True
            check.duration_ms = (time.time() - start_time) * 1000
            check.response_time_ms = check.duration_ms
            check.details = {
                'collections_count': len(collections.collections),
                'collections': [c.name for c in collections.collections]
            }
            
            logger.debug(f"Qdrant check successful for {connection.name}")
            
        except UnexpectedResponse as e:
            check.success = False
            check.error = str(e)
            check.error_type = "unexpected_response"
            check.status_code = getattr(e, 'status_code', None)
            check.duration_ms = (time.time() - start_time) * 1000
            
            logger.error(f"Qdrant check failed for {connection.name}: {e}")
            
        except Exception as e:
            check.success = False
            check.error = str(e)
            check.error_type = type(e).__name__
            check.duration_ms = (time.time() - start_time) * 1000
            
            logger.error(f"Qdrant check error for {connection.name}: {e}")
        
        return check


class MCPChecker(ConnectionChecker):
    """Checker for MCP Server connections."""
    
    async def check(self, connection: Connection) -> ConnectionCheck:
        """Check MCP Server connection."""
        start_time = time.time()
        check = ConnectionCheck(connection_id=connection.id)
        
        try:
            # Check if MCP server process is running
            result = subprocess.run(
                ["pgrep", "-f", "mcp-server-sqlite"],
                capture_output=True,
                text=True,
                timeout=connection.timeout_seconds
            )
            
            if result.returncode == 0:
                # Process is running
                pids = result.stdout.strip().split('\n')
                
                # Get process info
                process_info = []
                for pid in pids:
                    if pid:
                        try:
                            ps_result = subprocess.run(
                                ["ps", "-p", pid, "-o", "pid,ppid,user,comm,pcpu,pmem"],
                                capture_output=True,
                                text=True
                            )
                            if ps_result.returncode == 0:
                                process_info.append(ps_result.stdout.strip())
                        except:
                            pass
                
                check.success = True
                check.details = {
                    'process_count': len(pids),
                    'pids': pids,
                    'process_info': process_info
                }
                
                # Check MCP socket if available
                socket_path = connection.config.get('socket_path', '/tmp/mcp.sock')
                if socket_path:
                    try:
                        # Test socket connection
                        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                        sock.settimeout(1)
                        sock.connect(socket_path)
                        sock.close()
                        check.details['socket_status'] = 'connected'
                    except:
                        check.details['socket_status'] = 'not_available'
                
            else:
                # Process not running
                check.success = False
                check.error = "MCP Server process not found"
                check.error_type = "process_not_running"
            
            check.duration_ms = (time.time() - start_time) * 1000
            check.response_time_ms = check.duration_ms
            
        except subprocess.TimeoutExpired:
            check.success = False
            check.error = "Process check timeout"
            check.error_type = "timeout"
            check.duration_ms = (time.time() - start_time) * 1000
            
        except Exception as e:
            check.success = False
            check.error = str(e)
            check.error_type = type(e).__name__
            check.duration_ms = (time.time() - start_time) * 1000
            
            logger.error(f"MCP check error for {connection.name}: {e}")
        
        return check


class DatabaseChecker(ConnectionChecker):
    """Checker for database connections."""
    
    async def check(self, connection: Connection) -> ConnectionCheck:
        """Check database connection."""
        start_time = time.time()
        check = ConnectionCheck(connection_id=connection.id)
        
        db_type = connection.config.get('db_type', 'sqlite')
        
        try:
            if db_type == 'sqlite':
                # SQLite check
                import sqlite3
                
                db_path = connection.config.get('db_path', connection.url)
                conn = sqlite3.connect(db_path, timeout=connection.timeout_seconds)
                
                # Simple query
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                conn.close()
                
                check.success = True
                check.details = {
                    'db_type': 'sqlite',
                    'table_count': len(tables),
                    'tables': [t[0] for t in tables]
                }
                
            elif db_type == 'postgresql':
                # PostgreSQL check
                import asyncpg
                
                conn_str = connection.url or f"postgresql://{connection.host}:{connection.port}/{connection.config.get('database', 'postgres')}"
                
                conn = await asyncpg.connect(
                    conn_str,
                    timeout=connection.timeout_seconds
                )
                
                # Check version
                version = await conn.fetchval('SELECT version()')
                
                # Get database size
                db_size = await conn.fetchval("""
                    SELECT pg_database_size(current_database())
                """)
                
                await conn.close()
                
                check.success = True
                check.details = {
                    'db_type': 'postgresql',
                    'version': version,
                    'database_size_bytes': db_size
                }
                
            else:
                check.success = False
                check.error = f"Unsupported database type: {db_type}"
                check.error_type = "unsupported_db_type"
            
            check.duration_ms = (time.time() - start_time) * 1000
            check.response_time_ms = check.duration_ms
            
        except Exception as e:
            check.success = False
            check.error = str(e)
            check.error_type = type(e).__name__
            check.duration_ms = (time.time() - start_time) * 1000
            
            logger.error(f"Database check error for {connection.name}: {e}")
        
        return check


class ServiceChecker(ConnectionChecker):
    """Checker for internal service connections."""
    
    async def check(self, connection: Connection) -> ConnectionCheck:
        """Check service connection."""
        start_time = time.time()
        check = ConnectionCheck(connection_id=connection.id)
        
        service_name = connection.config.get('service_name', connection.name)
        check_method = connection.config.get('check_method', 'process')
        
        try:
            if check_method == 'process':
                # Check if service process is running
                result = subprocess.run(
                    ["pgrep", "-f", service_name],
                    capture_output=True,
                    text=True,
                    timeout=connection.timeout_seconds
                )
                
                check.success = result.returncode == 0
                if check.success:
                    pids = result.stdout.strip().split('\n')
                    check.details = {
                        'method': 'process',
                        'process_count': len(pids),
                        'pids': pids
                    }
                else:
                    check.error = f"Service process '{service_name}' not found"
                    check.error_type = "process_not_running"
                    
            elif check_method == 'port':
                # Check if service port is open
                port = connection.port or connection.config.get('port')
                host = connection.host or 'localhost'
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(connection.timeout_seconds)
                
                result = sock.connect_ex((host, port))
                sock.close()
                
                check.success = result == 0
                check.details = {
                    'method': 'port',
                    'host': host,
                    'port': port,
                    'reachable': check.success
                }
                
                if not check.success:
                    check.error = f"Port {port} not reachable on {host}"
                    check.error_type = "port_unreachable"
                    
            elif check_method == 'http_health':
                # Check HTTP health endpoint
                url = connection.url or f"http://{connection.host}:{connection.port}/health"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url,
                        timeout=aiohttp.ClientTimeout(total=connection.timeout_seconds)
                    ) as response:
                        check.success = response.status == 200
                        check.status_code = response.status
                        check.details = {
                            'method': 'http_health',
                            'url': url,
                            'status_code': response.status
                        }
                        
                        if response.status == 200:
                            try:
                                data = await response.json()
                                check.details['health_data'] = data
                            except:
                                pass
            
            check.duration_ms = (time.time() - start_time) * 1000
            check.response_time_ms = check.duration_ms
            
        except Exception as e:
            check.success = False
            check.error = str(e)
            check.error_type = type(e).__name__
            check.duration_ms = (time.time() - start_time) * 1000
            
            logger.error(f"Service check error for {connection.name}: {e}")
        
        return check


class HTTPChecker(ConnectionChecker):
    """Checker for HTTP endpoint connections."""
    
    async def check(self, connection: Connection) -> ConnectionCheck:
        """Check HTTP endpoint."""
        start_time = time.time()
        check = ConnectionCheck(connection_id=connection.id)
        
        url = connection.url
        if not url:
            protocol = connection.protocol or 'http'
            host = connection.host or 'localhost'
            port = connection.port or (443 if protocol == 'https' else 80)
            path = connection.config.get('path', '/')
            url = f"{protocol}://{host}:{port}{path}"
        
        try:
            async with aiohttp.ClientSession() as session:
                # Prepare request
                method = connection.config.get('method', 'GET')
                headers = connection.config.get('headers', {})
                
                # Add basic auth if configured
                auth = None
                if connection.config.get('username') and connection.config.get('password'):
                    auth = aiohttp.BasicAuth(
                        connection.config['username'],
                        connection.config['password']
                    )
                
                # Make request
                async with session.request(
                    method,
                    url,
                    headers=headers,
                    auth=auth,
                    timeout=aiohttp.ClientTimeout(total=connection.timeout_seconds),
                    ssl=connection.config.get('verify_ssl', True)
                ) as response:
                    check.status_code = response.status
                    check.response_time_ms = (time.time() - start_time) * 1000
                    
                    # Check expected status code
                    expected_status = connection.config.get('expected_status', 200)
                    if isinstance(expected_status, list):
                        check.success = response.status in expected_status
                    else:
                        check.success = response.status == expected_status
                    
                    check.details = {
                        'url': url,
                        'method': method,
                        'status_code': response.status,
                        'content_length': response.headers.get('Content-Length'),
                        'content_type': response.headers.get('Content-Type')
                    }
                    
                    # Check response content if configured
                    if check.success and connection.config.get('check_content'):
                        content = await response.text()
                        expected_content = connection.config.get('expected_content')
                        if expected_content and expected_content not in content:
                            check.success = False
                            check.error = "Expected content not found in response"
                            check.details['content_check'] = False
            
            check.duration_ms = (time.time() - start_time) * 1000
            
        except asyncio.TimeoutError:
            check.success = False
            check.error = f"Request timeout after {connection.timeout_seconds}s"
            check.error_type = "timeout"
            check.duration_ms = (time.time() - start_time) * 1000
            
        except Exception as e:
            check.success = False
            check.error = str(e)
            check.error_type = type(e).__name__
            check.duration_ms = (time.time() - start_time) * 1000
            
            logger.error(f"HTTP check error for {connection.name}: {e}")
        
        return check


# Checker registry
CHECKER_REGISTRY = {
    ConnectionType.QDRANT: QdrantChecker,
    ConnectionType.MCP_SERVER: MCPChecker,
    ConnectionType.DATABASE: DatabaseChecker,
    ConnectionType.SERVICE: ServiceChecker,
    ConnectionType.HTTP_ENDPOINT: HTTPChecker,
}


def get_checker(connection_type: ConnectionType) -> ConnectionChecker:
    """
    Get appropriate checker for connection type.
    
    Args:
        connection_type: Type of connection
        
    Returns:
        ConnectionChecker instance
        
    Raises:
        ValueError: If no checker available for type
    """
    checker_class = CHECKER_REGISTRY.get(connection_type)
    if not checker_class:
        raise ValueError(f"No checker available for connection type: {connection_type}")
    
    return checker_class()