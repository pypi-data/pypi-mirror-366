"""
MCP Server metrics analyzer for trends and anomaly detection.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import statistics
import numpy as np

from .models import MCPMetrics, MCPResourceUsage, MCPMethodStats
from .collector import MCPMetricsCollector

logger = logging.getLogger(__name__)


class TrendDirection(Enum):
    """Trend direction indicators."""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


class AnomalyType(Enum):
    """Types of anomalies."""
    HIGH_LATENCY = "high_latency"
    HIGH_ERROR_RATE = "high_error_rate"
    RESOURCE_SPIKE = "resource_spike"
    CONNECTION_SURGE = "connection_surge"
    MEMORY_LEAK = "memory_leak"
    THROUGHPUT_DROP = "throughput_drop"
    UNUSUAL_PATTERN = "unusual_pattern"


@dataclass
class MCPTrend:
    """Represents a trend in MCP metrics."""
    metric_name: str
    direction: TrendDirection
    current_value: float
    average_value: float
    change_rate: float  # Percentage change
    confidence: float  # 0-1 confidence in trend
    period_hours: int
    samples: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'metric_name': self.metric_name,
            'direction': self.direction.value,
            'current_value': self.current_value,
            'average_value': self.average_value,
            'change_rate': self.change_rate,
            'confidence': self.confidence,
            'period_hours': self.period_hours,
            'samples': self.samples
        }


@dataclass
class MCPAnomaly:
    """Represents an anomaly in MCP metrics."""
    anomaly_type: AnomalyType
    severity: str  # low, medium, high, critical
    metric_name: str
    current_value: float
    expected_value: float
    deviation: float  # Standard deviations from mean
    timestamp: datetime = field(default_factory=datetime.now)
    description: str = ""
    recommended_action: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'anomaly_type': self.anomaly_type.value,
            'severity': self.severity,
            'metric_name': self.metric_name,
            'current_value': self.current_value,
            'expected_value': self.expected_value,
            'deviation': self.deviation,
            'timestamp': self.timestamp.isoformat(),
            'description': self.description,
            'recommended_action': self.recommended_action
        }


@dataclass
class MCPPerformanceReport:
    """Comprehensive performance analysis report."""
    generated_at: datetime = field(default_factory=datetime.now)
    period_hours: int = 24
    
    # Summary metrics
    avg_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    total_requests: int = 0
    error_rate: float = 0.0
    
    # Resource utilization
    avg_cpu_percent: float = 0.0
    peak_cpu_percent: float = 0.0
    avg_memory_mb: float = 0.0
    peak_memory_mb: float = 0.0
    
    # Trends
    trends: List[MCPTrend] = field(default_factory=list)
    
    # Anomalies
    anomalies: List[MCPAnomaly] = field(default_factory=list)
    
    # Method performance
    slowest_methods: List[Dict[str, Any]] = field(default_factory=list)
    most_error_prone_methods: List[Dict[str, Any]] = field(default_factory=list)
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    
    # Health score (0-100)
    health_score: float = 100.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'generated_at': self.generated_at.isoformat(),
            'period_hours': self.period_hours,
            'summary': {
                'avg_response_time_ms': self.avg_response_time_ms,
                'p95_response_time_ms': self.p95_response_time_ms,
                'p99_response_time_ms': self.p99_response_time_ms,
                'total_requests': self.total_requests,
                'error_rate': self.error_rate
            },
            'resources': {
                'avg_cpu_percent': self.avg_cpu_percent,
                'peak_cpu_percent': self.peak_cpu_percent,
                'avg_memory_mb': self.avg_memory_mb,
                'peak_memory_mb': self.peak_memory_mb
            },
            'trends': [t.to_dict() for t in self.trends],
            'anomalies': [a.to_dict() for a in self.anomalies],
            'method_analysis': {
                'slowest_methods': self.slowest_methods,
                'most_error_prone': self.most_error_prone_methods
            },
            'recommendations': self.recommendations,
            'health_score': self.health_score
        }


class MCPAnalyzer:
    """
    Analyzes MCP metrics for trends, anomalies, and performance insights.
    """
    
    def __init__(self, collector: MCPMetricsCollector):
        """
        Initialize analyzer.
        
        Args:
            collector: MCP metrics collector instance
        """
        self.collector = collector
        
        # Thresholds for anomaly detection
        self.thresholds = {
            'high_latency_ms': 1000,
            'high_error_rate': 0.05,  # 5%
            'high_cpu_percent': 80,
            'high_memory_percent': 85,
            'connection_surge_factor': 3,  # 3x normal
            'memory_leak_growth_rate': 0.1  # 10% per hour
        }
        
        logger.info("MCPAnalyzer initialized")
    
    def analyze_trends(self, hours: int = 24) -> List[MCPTrend]:
        """
        Analyze trends in metrics over specified period.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            List of identified trends
        """
        trends = []
        
        # Get historical metrics
        metrics_history = self.collector.get_metrics_history(hours)
        if len(metrics_history) < 3:
            return trends  # Not enough data
        
        # Analyze response time trend
        response_times = [m.avg_response_time_ms for m in metrics_history if m.avg_response_time_ms > 0]
        if response_times:
            trend = self._analyze_metric_trend(
                "response_time",
                response_times,
                hours
            )
            if trend:
                trends.append(trend)
        
        # Analyze error rate trend
        error_rates = [m.error_rate for m in metrics_history]
        if error_rates:
            trend = self._analyze_metric_trend(
                "error_rate",
                error_rates,
                hours
            )
            if trend:
                trends.append(trend)
        
        # Analyze request rate trend
        request_rates = [m.requests_per_second for m in metrics_history]
        if request_rates:
            trend = self._analyze_metric_trend(
                "request_rate",
                request_rates,
                hours
            )
            if trend:
                trends.append(trend)
        
        # Analyze resource trends
        resource_history = self.collector.get_resource_history(hours)
        
        # CPU trend
        cpu_values = [r.cpu_percent for r in resource_history if r.cpu_percent > 0]
        if cpu_values:
            trend = self._analyze_metric_trend(
                "cpu_usage",
                cpu_values,
                hours
            )
            if trend:
                trends.append(trend)
        
        # Memory trend
        memory_values = [r.memory_used_mb for r in resource_history if r.memory_used_mb > 0]
        if memory_values:
            trend = self._analyze_metric_trend(
                "memory_usage",
                memory_values,
                hours
            )
            if trend:
                trends.append(trend)
        
        return trends
    
    def _analyze_metric_trend(self, metric_name: str, values: List[float], 
                            period_hours: int) -> Optional[MCPTrend]:
        """Analyze trend for a single metric."""
        if len(values) < 3:
            return None
        
        # Calculate basic statistics
        current_value = values[-1]
        average_value = statistics.mean(values)
        
        # Calculate trend using linear regression
        x = list(range(len(values)))
        y = values
        
        try:
            # Simple linear regression
            n = len(values)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(x[i] ** 2 for i in range(n))
            
            # Slope
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
            
            # Determine trend direction
            if abs(slope) < 0.01 * average_value:  # Less than 1% change
                direction = TrendDirection.STABLE
            elif slope > 0:
                direction = TrendDirection.INCREASING
            else:
                direction = TrendDirection.DECREASING
            
            # Check for volatility
            std_dev = statistics.stdev(values)
            if std_dev > 0.3 * average_value:  # High variance
                direction = TrendDirection.VOLATILE
            
            # Calculate change rate
            if average_value > 0:
                change_rate = ((current_value - average_value) / average_value) * 100
            else:
                change_rate = 0
            
            # Calculate confidence (based on R-squared)
            y_mean = sum_y / n
            ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))
            ss_res = sum((y[i] - (slope * x[i] + (y_mean - slope * sum_x / n))) ** 2 for i in range(n))
            
            if ss_tot > 0:
                r_squared = 1 - (ss_res / ss_tot)
                confidence = max(0, min(1, r_squared))
            else:
                confidence = 0
            
            return MCPTrend(
                metric_name=metric_name,
                direction=direction,
                current_value=current_value,
                average_value=average_value,
                change_rate=change_rate,
                confidence=confidence,
                period_hours=period_hours,
                samples=len(values)
            )
            
        except Exception as e:
            logger.error(f"Error analyzing trend for {metric_name}: {e}")
            return None
    
    def detect_anomalies(self) -> List[MCPAnomaly]:
        """
        Detect anomalies in current metrics.
        
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Get current metrics
        current = self.collector.get_current_metrics()
        
        # Get historical data for comparison
        history = self.collector.get_metrics_history(24)  # Last 24 hours
        
        if len(history) < 10:
            return anomalies  # Not enough historical data
        
        # Check for high latency
        anomaly = self._check_latency_anomaly(current, history)
        if anomaly:
            anomalies.append(anomaly)
        
        # Check for high error rate
        anomaly = self._check_error_rate_anomaly(current, history)
        if anomaly:
            anomalies.append(anomaly)
        
        # Check for resource anomalies
        resource_anomalies = self._check_resource_anomalies(current, history)
        anomalies.extend(resource_anomalies)
        
        # Check for connection anomalies
        anomaly = self._check_connection_anomaly(current, history)
        if anomaly:
            anomalies.append(anomaly)
        
        # Check for memory leak
        anomaly = self._check_memory_leak(history)
        if anomaly:
            anomalies.append(anomaly)
        
        # Check for throughput anomalies
        anomaly = self._check_throughput_anomaly(current, history)
        if anomaly:
            anomalies.append(anomaly)
        
        return anomalies
    
    def _check_latency_anomaly(self, current: MCPMetrics, 
                              history: List[MCPMetrics]) -> Optional[MCPAnomaly]:
        """Check for latency anomalies."""
        if current.avg_response_time_ms <= 0:
            return None
        
        # Calculate historical statistics
        historical_latencies = [m.avg_response_time_ms for m in history 
                               if m.avg_response_time_ms > 0]
        
        if not historical_latencies:
            return None
        
        mean_latency = statistics.mean(historical_latencies)
        std_latency = statistics.stdev(historical_latencies) if len(historical_latencies) > 1 else 0
        
        # Check if current latency is anomalous
        if std_latency > 0:
            deviation = (current.avg_response_time_ms - mean_latency) / std_latency
        else:
            deviation = 0
        
        # Check against absolute threshold and statistical deviation
        if (current.avg_response_time_ms > self.thresholds['high_latency_ms'] or 
            deviation > 3):  # More than 3 standard deviations
            
            severity = self._determine_severity(deviation, 2, 3, 5)
            
            return MCPAnomaly(
                anomaly_type=AnomalyType.HIGH_LATENCY,
                severity=severity,
                metric_name="avg_response_time_ms",
                current_value=current.avg_response_time_ms,
                expected_value=mean_latency,
                deviation=deviation,
                description=f"Response time {current.avg_response_time_ms:.0f}ms is "
                           f"{deviation:.1f} standard deviations above normal ({mean_latency:.0f}ms)",
                recommended_action="Check database performance, network latency, and server load"
            )
        
        return None
    
    def _check_error_rate_anomaly(self, current: MCPMetrics, 
                                history: List[MCPMetrics]) -> Optional[MCPAnomaly]:
        """Check for error rate anomalies."""
        if current.error_rate > self.thresholds['high_error_rate']:
            # Calculate historical average
            historical_rates = [m.error_rate for m in history]
            avg_error_rate = statistics.mean(historical_rates) if historical_rates else 0
            
            severity = "critical" if current.error_rate > 0.2 else "high"
            
            return MCPAnomaly(
                anomaly_type=AnomalyType.HIGH_ERROR_RATE,
                severity=severity,
                metric_name="error_rate",
                current_value=current.error_rate,
                expected_value=avg_error_rate,
                deviation=(current.error_rate - avg_error_rate) / max(avg_error_rate, 0.001),
                description=f"Error rate {current.error_rate:.1%} exceeds threshold",
                recommended_action="Review recent errors and check service dependencies"
            )
        
        return None
    
    def _check_resource_anomalies(self, current: MCPMetrics, 
                                history: List[MCPMetrics]) -> List[MCPAnomaly]:
        """Check for resource usage anomalies."""
        anomalies = []
        
        # CPU anomaly
        if current.resource_usage.cpu_percent > self.thresholds['high_cpu_percent']:
            anomalies.append(MCPAnomaly(
                anomaly_type=AnomalyType.RESOURCE_SPIKE,
                severity="high" if current.resource_usage.cpu_percent > 90 else "medium",
                metric_name="cpu_percent",
                current_value=current.resource_usage.cpu_percent,
                expected_value=self.thresholds['high_cpu_percent'],
                deviation=(current.resource_usage.cpu_percent - self.thresholds['high_cpu_percent']) / 10,
                description=f"CPU usage {current.resource_usage.cpu_percent:.1f}% exceeds threshold",
                recommended_action="Check for CPU-intensive operations or infinite loops"
            ))
        
        # Memory anomaly
        if current.resource_usage.memory_percent > self.thresholds['high_memory_percent']:
            anomalies.append(MCPAnomaly(
                anomaly_type=AnomalyType.RESOURCE_SPIKE,
                severity="critical" if current.resource_usage.memory_percent > 95 else "high",
                metric_name="memory_percent",
                current_value=current.resource_usage.memory_percent,
                expected_value=self.thresholds['high_memory_percent'],
                deviation=(current.resource_usage.memory_percent - self.thresholds['high_memory_percent']) / 10,
                description=f"Memory usage {current.resource_usage.memory_percent:.1f}% exceeds threshold",
                recommended_action="Check for memory leaks or excessive caching"
            ))
        
        return anomalies
    
    def _check_connection_anomaly(self, current: MCPMetrics, 
                                history: List[MCPMetrics]) -> Optional[MCPAnomaly]:
        """Check for connection anomalies."""
        if not history:
            return None
        
        # Calculate average active connections
        historical_connections = [m.active_sessions for m in history]
        avg_connections = statistics.mean(historical_connections) if historical_connections else 0
        
        if avg_connections > 0 and current.active_sessions > avg_connections * self.thresholds['connection_surge_factor']:
            return MCPAnomaly(
                anomaly_type=AnomalyType.CONNECTION_SURGE,
                severity="high",
                metric_name="active_connections",
                current_value=current.active_sessions,
                expected_value=avg_connections,
                deviation=(current.active_sessions - avg_connections) / max(avg_connections, 1),
                description=f"Active connections {current.active_sessions} is "
                           f"{current.active_sessions / max(avg_connections, 1):.1f}x normal",
                recommended_action="Check for connection leaks or DDoS attacks"
            )
        
        return None
    
    def _check_memory_leak(self, history: List[MCPMetrics]) -> Optional[MCPAnomaly]:
        """Check for potential memory leaks."""
        if len(history) < 10:
            return None
        
        # Get memory usage over time
        memory_values = []
        timestamps = []
        
        for metric in history:
            if metric.resource_usage.memory_used_mb > 0:
                memory_values.append(metric.resource_usage.memory_used_mb)
                timestamps.append(metric.timestamp.timestamp())
        
        if len(memory_values) < 10:
            return None
        
        # Check for consistent memory growth
        # Calculate hourly growth rate
        time_diff_hours = (timestamps[-1] - timestamps[0]) / 3600
        if time_diff_hours > 0:
            memory_growth = memory_values[-1] - memory_values[0]
            growth_rate = memory_growth / (memory_values[0] * time_diff_hours)
            
            if growth_rate > self.thresholds['memory_leak_growth_rate']:
                return MCPAnomaly(
                    anomaly_type=AnomalyType.MEMORY_LEAK,
                    severity="high",
                    metric_name="memory_growth_rate",
                    current_value=growth_rate * 100,
                    expected_value=0,
                    deviation=growth_rate / self.thresholds['memory_leak_growth_rate'],
                    description=f"Memory usage growing at {growth_rate * 100:.1f}% per hour",
                    recommended_action="Investigate potential memory leaks in the application"
                )
        
        return None
    
    def _check_throughput_anomaly(self, current: MCPMetrics, 
                                history: List[MCPMetrics]) -> Optional[MCPAnomaly]:
        """Check for throughput anomalies."""
        if not history or current.requests_per_second <= 0:
            return None
        
        # Calculate historical throughput
        historical_rps = [m.requests_per_second for m in history if m.requests_per_second > 0]
        
        if len(historical_rps) < 5:
            return None
        
        avg_rps = statistics.mean(historical_rps)
        
        # Check for significant drop in throughput
        if avg_rps > 0 and current.requests_per_second < avg_rps * 0.5:  # 50% drop
            return MCPAnomaly(
                anomaly_type=AnomalyType.THROUGHPUT_DROP,
                severity="high",
                metric_name="requests_per_second",
                current_value=current.requests_per_second,
                expected_value=avg_rps,
                deviation=(avg_rps - current.requests_per_second) / avg_rps,
                description=f"Request throughput {current.requests_per_second:.1f} RPS is "
                           f"{(1 - current.requests_per_second / avg_rps) * 100:.0f}% below normal",
                recommended_action="Check for service degradation or upstream issues"
            )
        
        return None
    
    def _determine_severity(self, value: float, low: float, medium: float, high: float) -> str:
        """Determine severity based on thresholds."""
        if value >= high:
            return "critical"
        elif value >= medium:
            return "high"
        elif value >= low:
            return "medium"
        else:
            return "low"
    
    def generate_performance_report(self, hours: int = 24) -> MCPPerformanceReport:
        """
        Generate comprehensive performance analysis report.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Performance report
        """
        report = MCPPerformanceReport(period_hours=hours)
        
        # Get metrics history
        metrics_history = self.collector.get_metrics_history(hours)
        
        if not metrics_history:
            return report
        
        # Calculate summary metrics
        response_times = [m.avg_response_time_ms for m in metrics_history if m.avg_response_time_ms > 0]
        if response_times:
            report.avg_response_time_ms = statistics.mean(response_times)
            sorted_times = sorted(response_times)
            report.p95_response_time_ms = sorted_times[int(len(sorted_times) * 0.95)]
            report.p99_response_time_ms = sorted_times[int(len(sorted_times) * 0.99)]
        
        report.total_requests = sum(m.total_requests for m in metrics_history)
        
        error_rates = [m.error_rate for m in metrics_history]
        report.error_rate = statistics.mean(error_rates) if error_rates else 0
        
        # Resource utilization
        resource_history = self.collector.get_resource_history(hours)
        if resource_history:
            cpu_values = [r.cpu_percent for r in resource_history if r.cpu_percent > 0]
            if cpu_values:
                report.avg_cpu_percent = statistics.mean(cpu_values)
                report.peak_cpu_percent = max(cpu_values)
            
            memory_values = [r.memory_used_mb for r in resource_history if r.memory_used_mb > 0]
            if memory_values:
                report.avg_memory_mb = statistics.mean(memory_values)
                report.peak_memory_mb = max(memory_values)
        
        # Add trends
        report.trends = self.analyze_trends(hours)
        
        # Add anomalies
        report.anomalies = self.detect_anomalies()
        
        # Analyze method performance
        method_stats = self.collector.get_method_stats()
        
        # Find slowest methods
        methods_by_response_time = sorted(
            [(name, stats.avg_response_time) for name, stats in method_stats.items() 
             if stats.avg_response_time > 0],
            key=lambda x: x[1],
            reverse=True
        )
        
        report.slowest_methods = [
            {'method': name, 'avg_response_time_ms': time}
            for name, time in methods_by_response_time[:5]
        ]
        
        # Find most error-prone methods
        methods_by_error_rate = sorted(
            [(name, stats.error_rate) for name, stats in method_stats.items() 
             if stats.total_calls > 10],  # Minimum calls for relevance
            key=lambda x: x[1],
            reverse=True
        )
        
        report.most_error_prone_methods = [
            {'method': name, 'error_rate': rate}
            for name, rate in methods_by_error_rate[:5]
            if rate > 0
        ]
        
        # Generate recommendations
        report.recommendations = self._generate_recommendations(report)
        
        # Calculate health score
        report.health_score = self._calculate_health_score(report)
        
        return report
    
    def _generate_recommendations(self, report: MCPPerformanceReport) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Check response time
        if report.avg_response_time_ms > 500:
            recommendations.append("Average response time is high. Consider optimizing slow queries and adding caching.")
        
        # Check error rate
        if report.error_rate > 0.02:
            recommendations.append("Error rate exceeds 2%. Review error logs and fix recurring issues.")
        
        # Check resource usage
        if report.avg_cpu_percent > 70:
            recommendations.append("High average CPU usage. Consider scaling horizontally or optimizing CPU-intensive operations.")
        
        if report.peak_memory_mb > report.avg_memory_mb * 2:
            recommendations.append("Memory usage spikes detected. Investigate memory allocation patterns.")
        
        # Check for anomalies
        critical_anomalies = [a for a in report.anomalies if a.severity in ['critical', 'high']]
        if critical_anomalies:
            recommendations.append(f"Address {len(critical_anomalies)} critical anomalies immediately.")
        
        # Check trends
        concerning_trends = [t for t in report.trends 
                           if t.direction == TrendDirection.INCREASING 
                           and t.metric_name in ['error_rate', 'response_time', 'memory_usage']]
        
        if concerning_trends:
            recommendations.append("Monitor increasing trends in error rate, response time, or memory usage.")
        
        # Method-specific recommendations
        if report.slowest_methods:
            slowest = report.slowest_methods[0]
            if slowest['avg_response_time_ms'] > 1000:
                recommendations.append(f"Optimize method '{slowest['method']}' which averages {slowest['avg_response_time_ms']:.0f}ms.")
        
        return recommendations
    
    def _calculate_health_score(self, report: MCPPerformanceReport) -> float:
        """Calculate overall health score (0-100)."""
        score = 100.0
        
        # Deduct for high response time
        if report.avg_response_time_ms > 1000:
            score -= 20
        elif report.avg_response_time_ms > 500:
            score -= 10
        
        # Deduct for error rate
        if report.error_rate > 0.05:
            score -= 25
        elif report.error_rate > 0.02:
            score -= 15
        elif report.error_rate > 0.01:
            score -= 5
        
        # Deduct for resource usage
        if report.avg_cpu_percent > 80:
            score -= 15
        elif report.avg_cpu_percent > 70:
            score -= 5
        
        # Deduct for anomalies
        critical_anomalies = sum(1 for a in report.anomalies if a.severity == 'critical')
        high_anomalies = sum(1 for a in report.anomalies if a.severity == 'high')
        
        score -= critical_anomalies * 10
        score -= high_anomalies * 5
        
        # Deduct for concerning trends
        bad_trends = sum(1 for t in report.trends 
                        if t.direction == TrendDirection.INCREASING 
                        and t.metric_name in ['error_rate', 'response_time', 'memory_usage'])
        
        score -= bad_trends * 5
        
        return max(0, min(100, score))