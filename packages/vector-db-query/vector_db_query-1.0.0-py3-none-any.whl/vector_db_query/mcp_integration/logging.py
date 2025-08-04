"""Logging and monitoring for MCP server."""

import json
import logging
import logging.handlers
import os
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .models import AuthToken


@dataclass
class RequestMetrics:
    """Metrics for a single request."""
    
    request_id: str
    tool_name: str
    client_id: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    success: bool = False
    error: Optional[str] = None
    token_count: Optional[int] = None
    result_count: Optional[int] = None
    
    def complete(self, success: bool, error: Optional[str] = None):
        """Mark request as complete."""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        self.success = success
        self.error = error


@dataclass
class ServerMetrics:
    """Server-wide metrics."""
    
    start_time: float = field(default_factory=time.time)
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens_processed: int = 0
    active_connections: int = 0
    
    # Per-tool metrics
    tool_requests: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    tool_errors: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    tool_durations: Dict[str, List[float]] = field(default_factory=lambda: defaultdict(list))
    
    # Per-client metrics
    client_requests: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    client_tokens: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    # Recent requests (for monitoring)
    recent_requests: deque = field(default_factory=lambda: deque(maxlen=100))
    
    @property
    def uptime_seconds(self) -> float:
        """Get server uptime in seconds."""
        return time.time() - self.start_time
    
    @property
    def success_rate(self) -> float:
        """Get request success rate."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def average_duration_ms(self) -> float:
        """Get average request duration."""
        all_durations = []
        for durations in self.tool_durations.values():
            all_durations.extend(durations)
        
        if not all_durations:
            return 0.0
        return sum(all_durations) / len(all_durations)
    
    def get_tool_stats(self, tool_name: str) -> Dict[str, Any]:
        """Get statistics for a specific tool."""
        requests = self.tool_requests.get(tool_name, 0)
        errors = self.tool_errors.get(tool_name, 0)
        durations = self.tool_durations.get(tool_name, [])
        
        return {
            "requests": requests,
            "errors": errors,
            "success_rate": ((requests - errors) / requests * 100) if requests > 0 else 0,
            "average_duration_ms": sum(durations) / len(durations) if durations else 0,
            "min_duration_ms": min(durations) if durations else 0,
            "max_duration_ms": max(durations) if durations else 0
        }


class MCPLogger:
    """Specialized logger for MCP server."""
    
    def __init__(
        self,
        name: str = "mcp_server",
        log_dir: Optional[Path] = None,
        enable_audit: bool = True,
        enable_metrics: bool = True
    ):
        """Initialize MCP logger.
        
        Args:
            name: Logger name
            log_dir: Directory for log files
            enable_audit: Enable audit logging
            enable_metrics: Enable metrics collection
        """
        self.logger = logging.getLogger(name)
        self.log_dir = log_dir or Path("logs")
        self.enable_audit = enable_audit
        self.enable_metrics = enable_metrics
        
        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup file handlers
        self._setup_handlers()
        
        # Initialize metrics
        self.metrics = ServerMetrics() if enable_metrics else None
        
        # Audit logger
        if enable_audit:
            self.audit_logger = logging.getLogger(f"{name}_audit")
            self._setup_audit_handler()
    
    def _setup_handlers(self):
        """Setup log handlers."""
        # Main log file
        main_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "mcp_server.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        main_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
        self.logger.addHandler(main_handler)
        
        # Error log file
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "mcp_errors.log",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n%(exc_info)s'
            )
        )
        self.logger.addHandler(error_handler)
    
    def _setup_audit_handler(self):
        """Setup audit log handler."""
        audit_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "mcp_audit.log",
            maxBytes=20 * 1024 * 1024,  # 20MB
            backupCount=10
        )
        
        # JSON formatter for structured audit logs
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_obj = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": record.levelname,
                    "event": record.getMessage(),
                    "details": getattr(record, "details", {})
                }
                return json.dumps(log_obj)
        
        audit_handler.setFormatter(JSONFormatter())
        self.audit_logger.addHandler(audit_handler)
        self.audit_logger.setLevel(logging.INFO)
    
    def log_request(
        self,
        request_id: str,
        tool_name: str,
        client_id: str,
        parameters: Dict[str, Any]
    ) -> RequestMetrics:
        """Log incoming request.
        
        Args:
            request_id: Unique request ID
            tool_name: Name of the tool being called
            client_id: Client making the request
            parameters: Request parameters
            
        Returns:
            RequestMetrics instance
        """
        # Create metrics
        metrics = RequestMetrics(
            request_id=request_id,
            tool_name=tool_name,
            client_id=client_id,
            start_time=time.time()
        )
        
        # Log request
        self.logger.info(
            f"Request {request_id}: {tool_name} from {client_id}"
        )
        
        # Audit log
        if self.enable_audit:
            self.audit_logger.info(
                "request_received",
                extra={
                    "details": {
                        "request_id": request_id,
                        "tool": tool_name,
                        "client_id": client_id,
                        "parameters": self._sanitize_params(parameters)
                    }
                }
            )
        
        # Update metrics
        if self.enable_metrics:
            self.metrics.total_requests += 1
            self.metrics.tool_requests[tool_name] += 1
            self.metrics.client_requests[client_id] += 1
        
        return metrics
    
    def log_response(
        self,
        metrics: RequestMetrics,
        response: Dict[str, Any],
        token_count: Optional[int] = None
    ):
        """Log response sent.
        
        Args:
            metrics: Request metrics
            response: Response data
            token_count: Number of tokens in response
        """
        # Complete metrics
        metrics.complete(success=True)
        metrics.token_count = token_count
        metrics.result_count = len(response.get("results", []))
        
        # Log response
        self.logger.info(
            f"Response {metrics.request_id}: Success in {metrics.duration_ms:.2f}ms"
        )
        
        # Audit log
        if self.enable_audit:
            self.audit_logger.info(
                "response_sent",
                extra={
                    "details": {
                        "request_id": metrics.request_id,
                        "duration_ms": metrics.duration_ms,
                        "token_count": token_count,
                        "result_count": metrics.result_count
                    }
                }
            )
        
        # Update metrics
        if self.enable_metrics:
            self.metrics.successful_requests += 1
            self.metrics.tool_durations[metrics.tool_name].append(metrics.duration_ms)
            
            if token_count:
                self.metrics.total_tokens_processed += token_count
                self.metrics.client_tokens[metrics.client_id] += token_count
            
            self.metrics.recent_requests.append(metrics)
    
    def log_error(
        self,
        metrics: RequestMetrics,
        error: Exception,
        error_code: Optional[str] = None
    ):
        """Log error response.
        
        Args:
            metrics: Request metrics
            error: Exception that occurred
            error_code: Optional error code
        """
        # Complete metrics
        metrics.complete(success=False, error=str(error))
        
        # Log error
        self.logger.error(
            f"Error {metrics.request_id}: {error.__class__.__name__}: {str(error)}",
            exc_info=True
        )
        
        # Audit log
        if self.enable_audit:
            self.audit_logger.error(
                "request_error",
                extra={
                    "details": {
                        "request_id": metrics.request_id,
                        "error_type": error.__class__.__name__,
                        "error_message": str(error),
                        "error_code": error_code,
                        "duration_ms": metrics.duration_ms
                    }
                }
            )
        
        # Update metrics
        if self.enable_metrics:
            self.metrics.failed_requests += 1
            self.metrics.tool_errors[metrics.tool_name] += 1
            self.metrics.recent_requests.append(metrics)
    
    def log_auth_event(
        self,
        event_type: str,
        client_id: str,
        success: bool,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log authentication event.
        
        Args:
            event_type: Type of auth event
            client_id: Client ID
            success: Whether auth succeeded
            details: Additional details
        """
        level = logging.INFO if success else logging.WARNING
        
        self.logger.log(
            level,
            f"Auth {event_type}: {client_id} - {'Success' if success else 'Failed'}"
        )
        
        if self.enable_audit:
            self.audit_logger.log(
                level,
                f"auth_{event_type}",
                extra={
                    "details": {
                        "client_id": client_id,
                        "success": success,
                        **(details or {})
                    }
                }
            )
    
    def log_connection_event(
        self,
        event_type: str,
        client_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log connection event.
        
        Args:
            event_type: Type of connection event
            client_id: Optional client ID
            details: Additional details
        """
        self.logger.info(f"Connection {event_type}: {client_id or 'unknown'}")
        
        if self.enable_metrics:
            if event_type == "connected":
                self.metrics.active_connections += 1
            elif event_type == "disconnected":
                self.metrics.active_connections = max(0, self.metrics.active_connections - 1)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get current metrics summary.
        
        Returns:
            Metrics summary dictionary
        """
        if not self.enable_metrics:
            return {}
        
        uptime = timedelta(seconds=int(self.metrics.uptime_seconds))
        
        return {
            "server": {
                "uptime": str(uptime),
                "active_connections": self.metrics.active_connections,
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "success_rate": f"{self.metrics.success_rate:.2f}%",
                "average_duration_ms": f"{self.metrics.average_duration_ms:.2f}",
                "total_tokens_processed": self.metrics.total_tokens_processed
            },
            "tools": {
                tool: self.metrics.get_tool_stats(tool)
                for tool in self.metrics.tool_requests.keys()
            },
            "top_clients": self._get_top_clients(5),
            "recent_errors": self._get_recent_errors(10)
        }
    
    def _get_top_clients(self, limit: int) -> List[Dict[str, Any]]:
        """Get top clients by request count."""
        if not self.enable_metrics:
            return []
        
        sorted_clients = sorted(
            self.metrics.client_requests.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [
            {
                "client_id": client_id,
                "requests": count,
                "tokens": self.metrics.client_tokens.get(client_id, 0)
            }
            for client_id, count in sorted_clients
        ]
    
    def _get_recent_errors(self, limit: int) -> List[Dict[str, Any]]:
        """Get recent error requests."""
        if not self.enable_metrics:
            return []
        
        errors = [
            {
                "request_id": req.request_id,
                "tool": req.tool_name,
                "client_id": req.client_id,
                "error": req.error,
                "timestamp": datetime.fromtimestamp(req.start_time).isoformat()
            }
            for req in self.metrics.recent_requests
            if not req.success
        ]
        
        return errors[-limit:]
    
    def _sanitize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize parameters for logging."""
        sanitized = {}
        sensitive_keys = {"password", "secret", "token", "key", "auth"}
        
        for key, value in params.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, str) and len(value) > 100:
                sanitized[key] = value[:100] + "..."
            else:
                sanitized[key] = value
        
        return sanitized
    
    def export_metrics(self, output_path: Path):
        """Export metrics to file.
        
        Args:
            output_path: Path to save metrics
        """
        if not self.enable_metrics:
            return
        
        metrics_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": self.get_metrics_summary(),
            "raw_metrics": {
                "start_time": self.metrics.start_time,
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "total_tokens_processed": self.metrics.total_tokens_processed,
                "tool_requests": dict(self.metrics.tool_requests),
                "tool_errors": dict(self.metrics.tool_errors),
                "client_requests": dict(self.metrics.client_requests),
                "client_tokens": dict(self.metrics.client_tokens)
            }
        }
        
        with open(output_path, "w") as f:
            json.dump(metrics_data, f, indent=2)
        
        self.logger.info(f"Metrics exported to: {output_path}")