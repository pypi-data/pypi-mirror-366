"""
Monitoring configuration for the Text2SQL-LTM library.

This module provides comprehensive monitoring and observability settings
including metrics, logging, tracing, and alerting configuration.
"""

from __future__ import annotations

from typing import Optional, Dict, Any, List, Set
from enum import Enum
from pathlib import Path

from pydantic import Field, validator, root_validator

from .base import BaseConfig
from ..types import LogLevel
from ..exceptions import InvalidConfigurationError


class MetricsBackend(str, Enum):
    """Supported metrics backends."""
    PROMETHEUS = "prometheus"
    STATSD = "statsd"
    DATADOG = "datadog"
    CLOUDWATCH = "cloudwatch"
    CUSTOM = "custom"
    DISABLED = "disabled"


class TracingBackend(str, Enum):
    """Supported tracing backends."""
    JAEGER = "jaeger"
    ZIPKIN = "zipkin"
    DATADOG = "datadog"
    OPENTELEMETRY = "opentelemetry"
    DISABLED = "disabled"


class AlertingBackend(str, Enum):
    """Supported alerting backends."""
    SLACK = "slack"
    EMAIL = "email"
    WEBHOOK = "webhook"
    PAGERDUTY = "pagerduty"
    CUSTOM = "custom"
    DISABLED = "disabled"


class LogFormat(str, Enum):
    """Log format options."""
    JSON = "json"
    TEXT = "text"
    STRUCTURED = "structured"


class MonitoringConfig(BaseConfig):
    """
    Monitoring and observability configuration for the Text2SQL-LTM library.
    
    This configuration handles all monitoring aspects including metrics collection,
    logging, distributed tracing, alerting, and health checks.
    """
    
    # General Monitoring Settings
    monitoring_enabled: bool = Field(
        True,
        description="Enable monitoring and observability features"
    )
    service_name: str = Field(
        "text2sql-ltm",
        description="Service name for monitoring identification"
    )
    service_version: str = Field(
        "1.0.0",
        description="Service version for monitoring"
    )
    environment: str = Field(
        "production",
        description="Environment name (development, staging, production)"
    )
    
    # Metrics Configuration
    metrics_enabled: bool = Field(
        True,
        description="Enable metrics collection"
    )
    metrics_backend: MetricsBackend = Field(
        MetricsBackend.PROMETHEUS,
        description="Metrics backend system"
    )
    metrics_port: int = Field(
        9090,
        ge=1024,
        le=65535,
        description="Port for metrics server"
    )
    metrics_path: str = Field(
        "/metrics",
        description="HTTP path for metrics endpoint"
    )
    metrics_collection_interval: int = Field(
        15,
        ge=1,
        le=300,
        description="Metrics collection interval in seconds"
    )
    metrics_retention_days: int = Field(
        30,
        ge=1,
        le=365,
        description="Metrics retention period in days"
    )
    
    # Custom Metrics Settings
    custom_metrics_enabled: bool = Field(
        True,
        description="Enable custom application metrics"
    )
    business_metrics_enabled: bool = Field(
        True,
        description="Enable business-specific metrics"
    )
    performance_metrics_enabled: bool = Field(
        True,
        description="Enable detailed performance metrics"
    )
    memory_metrics_enabled: bool = Field(
        True,
        description="Enable memory usage metrics"
    )
    
    # Logging Configuration
    logging_enabled: bool = Field(
        True,
        description="Enable application logging"
    )
    log_level: LogLevel = Field(
        LogLevel.INFO,
        description="Minimum log level"
    )
    log_format: LogFormat = Field(
        LogFormat.JSON,
        description="Log output format"
    )
    log_file_path: Optional[Path] = Field(
        None,
        description="Path to log file (None for stdout)"
    )
    log_rotation_enabled: bool = Field(
        True,
        description="Enable log file rotation"
    )
    log_max_size_mb: int = Field(
        100,
        ge=1,
        le=1024,
        description="Maximum log file size in MB before rotation"
    )
    log_backup_count: int = Field(
        5,
        ge=1,
        le=100,
        description="Number of backup log files to keep"
    )
    
    # Structured Logging
    structured_logging: bool = Field(
        True,
        description="Enable structured logging with consistent fields"
    )
    log_correlation_id: bool = Field(
        True,
        description="Include correlation IDs in logs"
    )
    log_user_context: bool = Field(
        False,
        description="Include user context in logs (be careful with privacy)"
    )
    log_request_details: bool = Field(
        True,
        description="Log request details for debugging"
    )
    log_response_details: bool = Field(
        False,
        description="Log response details (can be verbose)"
    )
    
    # Distributed Tracing
    tracing_enabled: bool = Field(
        True,
        description="Enable distributed tracing"
    )
    tracing_backend: TracingBackend = Field(
        TracingBackend.JAEGER,
        description="Tracing backend system"
    )
    tracing_sample_rate: float = Field(
        0.1,
        ge=0.0,
        le=1.0,
        description="Tracing sample rate (0.0 to 1.0)"
    )
    tracing_endpoint: Optional[str] = Field(
        None,
        description="Tracing backend endpoint URL"
    )
    trace_sensitive_operations: bool = Field(
        False,
        description="Include sensitive operations in traces"
    )
    
    # Health Checks
    health_checks_enabled: bool = Field(
        True,
        description="Enable health check endpoints"
    )
    health_check_port: int = Field(
        8080,
        ge=1024,
        le=65535,
        description="Port for health check endpoints"
    )
    health_check_path: str = Field(
        "/health",
        description="HTTP path for health check endpoint"
    )
    readiness_check_path: str = Field(
        "/ready",
        description="HTTP path for readiness check endpoint"
    )
    liveness_check_path: str = Field(
        "/live",
        description="HTTP path for liveness check endpoint"
    )
    health_check_timeout: int = Field(
        5,
        ge=1,
        le=60,
        description="Health check timeout in seconds"
    )
    
    # Alerting Configuration
    alerting_enabled: bool = Field(
        True,
        description="Enable alerting system"
    )
    alerting_backend: AlertingBackend = Field(
        AlertingBackend.DISABLED,  # Default to disabled to avoid validation issues
        description="Alerting backend system"
    )
    alert_webhook_url: Optional[str] = Field(
        None,
        description="Webhook URL for alerts"
    )
    alert_email_recipients: List[str] = Field(
        default_factory=list,
        description="Email recipients for alerts"
    )
    alert_slack_webhook: Optional[str] = Field(
        None,
        description="Slack webhook URL for alerts"
    )
    
    # Alert Thresholds
    error_rate_threshold: float = Field(
        0.05,
        ge=0.0,
        le=1.0,
        description="Error rate threshold for alerts (5%)"
    )
    response_time_threshold_ms: int = Field(
        5000,
        ge=100,
        le=60000,
        description="Response time threshold in milliseconds"
    )
    memory_usage_threshold: float = Field(
        0.85,
        ge=0.1,
        le=0.99,
        description="Memory usage threshold for alerts"
    )
    cpu_usage_threshold: float = Field(
        0.80,
        ge=0.1,
        le=0.99,
        description="CPU usage threshold for alerts"
    )
    disk_usage_threshold: float = Field(
        0.90,
        ge=0.1,
        le=0.99,
        description="Disk usage threshold for alerts"
    )
    
    # Performance Monitoring
    performance_monitoring_enabled: bool = Field(
        True,
        description="Enable performance monitoring"
    )
    slow_query_threshold_ms: int = Field(
        1000,
        ge=100,
        le=60000,
        description="Slow query threshold in milliseconds"
    )
    memory_leak_detection: bool = Field(
        True,
        description="Enable memory leak detection"
    )
    deadlock_detection: bool = Field(
        True,
        description="Enable deadlock detection"
    )
    
    # Security Monitoring
    security_monitoring_enabled: bool = Field(
        True,
        description="Enable security event monitoring"
    )
    failed_auth_threshold: int = Field(
        5,
        ge=1,
        le=100,
        description="Failed authentication attempts threshold"
    )
    suspicious_activity_detection: bool = Field(
        True,
        description="Enable suspicious activity detection"
    )
    audit_log_monitoring: bool = Field(
        True,
        description="Enable audit log monitoring"
    )
    
    # Data Export and Retention
    export_metrics_enabled: bool = Field(
        False,
        description="Enable metrics export to external systems"
    )
    export_logs_enabled: bool = Field(
        False,
        description="Enable log export to external systems"
    )
    data_retention_policy: Dict[str, int] = Field(
        default_factory=lambda: {
            "metrics": 30,
            "logs": 7,
            "traces": 3,
            "alerts": 90
        },
        description="Data retention policy in days for different data types"
    )
    
    @classmethod
    def get_config_section(cls) -> str:
        """Get the configuration section name."""
        return "monitoring"
    
    def get_sensitive_fields(self) -> List[str]:
        """Get list of field names that contain sensitive data."""
        return [
            "alert_webhook_url",
            "alert_slack_webhook",
            "tracing_endpoint"
        ]
    
    @validator('metrics_port', 'health_check_port')
    def validate_ports(cls, v: int) -> int:
        """Validate port numbers."""
        if v < 1024 or v > 65535:
            raise ValueError("Port must be between 1024 and 65535")
        return v
    
    @validator('alert_email_recipients')
    def validate_email_recipients(cls, v: List[str]) -> List[str]:
        """Validate email addresses."""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        for email in v:
            if not re.match(email_pattern, email):
                raise ValueError(f"Invalid email address: {email}")
        
        return v
    
    @validator('alert_webhook_url', 'alert_slack_webhook', 'tracing_endpoint')
    def validate_urls(cls, v: Optional[str]) -> Optional[str]:
        """Validate URL formats."""
        if v is None:
            return v
        
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        
        return v
    
    @validator('log_file_path')
    def validate_log_file_path(cls, v: Optional[Path]) -> Optional[Path]:
        """Validate log file path."""
        if v is None:
            return v
        
        # Ensure parent directory exists or can be created
        try:
            v.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Cannot create log directory: {e}")
        
        return v
    
    @root_validator(skip_on_failure=True)
    def validate_alerting_config(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate alerting configuration consistency."""
        alerting_enabled = values.get('alerting_enabled', False)
        backend = values.get('alerting_backend')
        
        if alerting_enabled and backend != AlertingBackend.DISABLED:
            webhook_url = values.get('alert_webhook_url')
            email_recipients = values.get('alert_email_recipients', [])
            slack_webhook = values.get('alert_slack_webhook')
            
            if backend == AlertingBackend.WEBHOOK and not webhook_url:
                raise ValueError("Webhook URL required when using webhook alerting")
            elif backend == AlertingBackend.EMAIL and not email_recipients:
                raise ValueError("Email recipients required when using email alerting")
            elif backend == AlertingBackend.SLACK and not slack_webhook:
                raise ValueError("Slack webhook required when using Slack alerting")
        
        return values
    
    @root_validator(skip_on_failure=True)
    def validate_port_conflicts(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that ports don't conflict."""
        metrics_port = values.get('metrics_port')
        health_port = values.get('health_check_port')
        
        if metrics_port == health_port:
            raise ValueError("Metrics port and health check port cannot be the same")
        
        return values
    
    def validate_config(self) -> None:
        """Perform additional validation after initialization."""
        # Validate threshold relationships
        if self.tracing_sample_rate > 0.5 and self.environment == "production":
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="tracing_sample_rate",
                reason="High tracing sample rate may impact performance in production"
            )
        
        # Validate retention policy
        for data_type, days in self.data_retention_policy.items():
            if days < 1:
                raise InvalidConfigurationError(
                    config_section=self.get_config_section(),
                    config_key="data_retention_policy",
                    reason=f"Retention period for {data_type} must be at least 1 day"
                )
    
    def validate_production_ready(self) -> None:
        """Validate that configuration is production-ready."""
        if not self.monitoring_enabled:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="monitoring_enabled",
                reason="Monitoring must be enabled in production"
            )
        
        if not self.health_checks_enabled:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="health_checks_enabled",
                reason="Health checks must be enabled in production"
            )
        
        if not self.alerting_enabled:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="alerting_enabled",
                reason="Alerting must be enabled in production"
            )
        
        if self.log_level == LogLevel.DEBUG:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="log_level",
                reason="Debug logging should not be used in production"
            )
        
        if self.log_response_details:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="log_response_details",
                reason="Response detail logging should be disabled in production"
            )
    
    def get_metrics_labels(self) -> Dict[str, str]:
        """Get standard metrics labels."""
        return {
            "service": self.service_name,
            "version": self.service_version,
            "environment": self.environment,
        }
    
    def should_trace_operation(self, operation_name: str) -> bool:
        """Determine if an operation should be traced."""
        if not self.tracing_enabled:
            return False
        
        # Sample based on configured rate
        import random
        if random.random() > self.tracing_sample_rate:
            return False
        
        # Skip sensitive operations if configured
        if not self.trace_sensitive_operations:
            sensitive_operations = {"login", "authenticate", "decrypt", "encrypt"}
            if operation_name.lower() in sensitive_operations:
                return False
        
        return True
    
    def is_slow_query(self, duration_ms: int) -> bool:
        """Check if a query duration exceeds the slow query threshold."""
        return duration_ms > self.slow_query_threshold_ms
