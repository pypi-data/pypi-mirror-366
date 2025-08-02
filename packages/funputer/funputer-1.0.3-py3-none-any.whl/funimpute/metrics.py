"""
Prometheus metrics for observability and monitoring.
"""

import time
from typing import Dict, Any
from prometheus_client import Gauge, Counter, Histogram, start_http_server
import threading


class MetricsCollector:
    """Prometheus metrics collector for imputation analysis."""
    
    def __init__(self, port: int = 8001):
        self.port = port
        self._server_started = False
        self._lock = threading.Lock()
        
        # Define metrics
        self.columns_processed = Counter(
            'funimpute_columns_processed_total',
            'Total number of columns processed',
            ['data_type', 'mechanism']
        )
        
        self.missing_values_total = Gauge(
            'funimpute_missing_values_total',
            'Total number of missing values across all columns'
        )
        
        self.outliers_total = Gauge(
            'funimpute_outliers_total',
            'Total number of outliers detected across all columns'
        )
        
        self.analysis_duration = Histogram(
            'funimpute_analysis_duration_seconds',
            'Time spent analyzing each column',
            ['column_name', 'data_type'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
        )
        
        self.total_analysis_duration = Gauge(
            'funimpute_total_analysis_duration_seconds',
            'Total time spent on complete analysis'
        )
        
        self.confidence_score = Histogram(
            'funimpute_confidence_score',
            'Distribution of confidence scores for imputation proposals',
            ['method', 'mechanism'],
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        )
        
        self.data_quality_score = Gauge(
            'funimpute_data_quality_score',
            'Overall data quality score (0-1)',
            ['dataset']
        )
    
    def start_server(self) -> None:
        """Start the Prometheus metrics server."""
        with self._lock:
            if not self._server_started:
                try:
                    start_http_server(self.port)
                    self._server_started = True
                    print(f"Prometheus metrics server started on port {self.port}")
                except Exception as e:
                    print(f"Failed to start metrics server on port {self.port}: {e}")
    
    def record_column_processed(self, data_type: str, mechanism: str) -> None:
        """Record that a column has been processed."""
        self.columns_processed.labels(data_type=data_type, mechanism=mechanism).inc()
    
    def update_missing_values_total(self, count: int) -> None:
        """Update total missing values count."""
        self.missing_values_total.set(count)
    
    def update_outliers_total(self, count: int) -> None:
        """Update total outliers count."""
        self.outliers_total.set(count)
    
    def record_analysis_duration(self, column_name: str, data_type: str, duration: float) -> None:
        """Record analysis duration for a column."""
        self.analysis_duration.labels(column_name=column_name, data_type=data_type).observe(duration)
    
    def update_total_analysis_duration(self, duration: float) -> None:
        """Update total analysis duration."""
        self.total_analysis_duration.set(duration)
    
    def record_confidence_score(self, method: str, mechanism: str, score: float) -> None:
        """Record confidence score for an imputation proposal."""
        self.confidence_score.labels(method=method, mechanism=mechanism).observe(score)
    
    def update_data_quality_score(self, dataset: str, score: float) -> None:
        """Update overall data quality score."""
        self.data_quality_score.labels(dataset=dataset).set(score)
    
    def calculate_data_quality_score(self, analysis_results: list) -> float:
        """
        Calculate overall data quality score based on analysis results.
        
        Args:
            analysis_results: List of column analysis results
            
        Returns:
            Data quality score between 0 and 1
        """
        if not analysis_results:
            return 0.0
        
        total_score = 0.0
        
        for result in analysis_results:
            column_score = 1.0
            
            # Penalize for high missing percentage
            missing_pct = result.missingness_analysis.missing_percentage
            if missing_pct > 0.5:
                column_score -= 0.4
            elif missing_pct > 0.2:
                column_score -= 0.2
            elif missing_pct > 0.1:
                column_score -= 0.1
            
            # Penalize for high outlier percentage
            outlier_pct = result.outlier_analysis.outlier_percentage
            if outlier_pct > 0.2:
                column_score -= 0.3
            elif outlier_pct > 0.1:
                column_score -= 0.15
            elif outlier_pct > 0.05:
                column_score -= 0.05
            
            # Bonus for high confidence imputation proposals
            confidence = result.imputation_proposal.confidence_score
            if confidence > 0.8:
                column_score += 0.1
            elif confidence < 0.4:
                column_score -= 0.1
            
            # Ensure column score is within bounds
            column_score = max(0.0, min(1.0, column_score))
            total_score += column_score
        
        return total_score / len(analysis_results)


# Global metrics collector instance
_metrics_collector = None


def get_metrics_collector(port: int = 8001) -> MetricsCollector:
    """Get or create the global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector(port)
    return _metrics_collector


def start_metrics_server(port: int = 8001) -> None:
    """Start the Prometheus metrics server."""
    collector = get_metrics_collector(port)
    collector.start_server()


class MetricsContext:
    """Context manager for timing operations and recording metrics."""
    
    def __init__(self, column_name: str, data_type: str):
        self.column_name = column_name
        self.data_type = data_type
        self.start_time = None
        self.metrics = get_metrics_collector()
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration = time.time() - self.start_time
            self.metrics.record_analysis_duration(
                self.column_name, self.data_type, duration
            )
