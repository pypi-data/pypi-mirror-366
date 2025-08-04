"""
Security configuration for the Text2SQL-LTM library.

This module provides comprehensive security settings including
authentication, authorization, encryption, and compliance features.
"""

from __future__ import annotations

from typing import Optional, Dict, Any, List, Set
from enum import Enum
from pathlib import Path
import secrets

from pydantic import Field, validator, root_validator

from .base import BaseConfig
from ..exceptions import InvalidConfigurationError


class EncryptionMethod(str, Enum):
    """Supported encryption methods."""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    CHACHA20_POLY1305 = "chacha20_poly1305"


class AuthenticationMethod(str, Enum):
    """Supported authentication methods."""
    API_KEY = "api_key"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    BASIC_AUTH = "basic_auth"
    CUSTOM = "custom"


class HashingAlgorithm(str, Enum):
    """Supported hashing algorithms."""
    BCRYPT = "bcrypt"
    SCRYPT = "scrypt"
    ARGON2 = "argon2"
    PBKDF2 = "pbkdf2"


class SecurityConfig(BaseConfig):
    """
    Security and privacy configuration for the Text2SQL-LTM library.
    
    This configuration handles all security aspects including authentication,
    authorization, encryption, data protection, and compliance.
    """
    
    # Authentication Settings
    require_authentication: bool = Field(
        True, 
        description="Require user authentication for all operations"
    )
    authentication_method: AuthenticationMethod = Field(
        AuthenticationMethod.API_KEY,
        description="Primary authentication method"
    )
    session_secret_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Secret key for session management"
    )
    api_key_length: int = Field(
        32,
        ge=16,
        le=128,
        description="Length of generated API keys"
    )
    
    # Token and Session Settings
    token_expiry_hours: int = Field(
        24, 
        ge=1,
        le=8760,  # 1 year
        description="Token expiry time in hours"
    )
    refresh_token_expiry_days: int = Field(
        30,
        ge=1,
        le=365,
        description="Refresh token expiry time in days"
    )
    session_timeout_minutes: int = Field(
        60,
        ge=5,
        le=1440,  # 24 hours
        description="Session timeout in minutes"
    )
    max_sessions_per_user: int = Field(
        5,
        ge=1,
        le=100,
        description="Maximum concurrent sessions per user"
    )
    
    # Encryption Settings
    encrypt_memories: bool = Field(
        True, 
        description="Encrypt stored memories"
    )
    encryption_method: EncryptionMethod = Field(
        EncryptionMethod.AES_256_GCM,
        description="Encryption method for data at rest"
    )
    encryption_key: Optional[str] = Field(
        None, 
        description="Master encryption key (auto-generated if not provided)"
    )
    key_rotation_days: int = Field(
        90,
        ge=1,
        le=365,
        description="Encryption key rotation period in days"
    )
    encrypt_in_transit: bool = Field(
        True,
        description="Require TLS/SSL for all communications"
    )
    
    # Data Protection and Privacy
    hash_user_ids: bool = Field(
        True, 
        description="Hash user IDs for privacy protection"
    )
    hashing_algorithm: HashingAlgorithm = Field(
        HashingAlgorithm.ARGON2,
        description="Algorithm for hashing sensitive data"
    )
    salt_length: int = Field(
        16,
        ge=8,
        le=64,
        description="Salt length for hashing operations"
    )
    anonymize_logs: bool = Field(
        True,
        description="Anonymize user data in logs"
    )
    data_masking_enabled: bool = Field(
        True,
        description="Enable data masking for sensitive fields"
    )
    
    # Access Control and Authorization
    enable_rbac: bool = Field(
        True,
        description="Enable role-based access control"
    )
    default_user_role: str = Field(
        "user",
        description="Default role for new users"
    )
    admin_roles: Set[str] = Field(
        default_factory=lambda: {"admin", "superuser"},
        description="Set of administrative roles"
    )
    require_user_consent: bool = Field(
        True,
        description="Require explicit user consent for data processing"
    )
    
    # Rate Limiting and DDoS Protection
    rate_limiting_enabled: bool = Field(
        True, 
        description="Enable rate limiting"
    )
    max_requests_per_minute: int = Field(
        60,
        ge=1,
        le=10000,
        description="Maximum requests per minute per user"
    )
    max_requests_per_hour: int = Field(
        3600,  # 60 * 60 to be consistent with per-minute limit
        ge=10,
        le=100000,
        description="Maximum requests per hour per user"
    )
    burst_limit: int = Field(
        10,
        ge=1,
        le=100,
        description="Burst limit for rate limiting"
    )
    ip_whitelist: List[str] = Field(
        default_factory=list, 
        description="IP addresses exempt from rate limiting"
    )
    ip_blacklist: List[str] = Field(
        default_factory=list,
        description="Blocked IP addresses"
    )
    
    # Audit and Compliance
    audit_logging: bool = Field(
        True, 
        description="Enable comprehensive audit logging"
    )
    audit_log_retention_days: int = Field(
        365,
        ge=30,
        le=2555,  # 7 years
        description="Audit log retention period in days"
    )
    gdpr_compliance: bool = Field(
        True, 
        description="Enable GDPR compliance features"
    )
    ccpa_compliance: bool = Field(
        True,
        description="Enable CCPA compliance features"
    )
    data_export_enabled: bool = Field(
        True, 
        description="Enable user data export functionality"
    )
    data_deletion_enabled: bool = Field(
        True, 
        description="Enable user data deletion functionality"
    )
    right_to_be_forgotten: bool = Field(
        True,
        description="Enable right to be forgotten compliance"
    )
    
    # Security Headers and Policies
    cors_origins: List[str] = Field(
        default_factory=list, 
        description="CORS allowed origins"
    )
    cors_allow_credentials: bool = Field(
        False,
        description="Allow credentials in CORS requests"
    )
    content_security_policy: Optional[str] = Field(
        None, 
        description="Content Security Policy header"
    )
    hsts_max_age: int = Field(
        31536000,  # 1 year
        ge=0,
        description="HTTP Strict Transport Security max age"
    )
    
    # Vulnerability Protection
    enable_sql_injection_protection: bool = Field(
        True,
        description="Enable SQL injection protection"
    )
    enable_xss_protection: bool = Field(
        True,
        description="Enable XSS protection"
    )
    enable_csrf_protection: bool = Field(
        True,
        description="Enable CSRF protection"
    )
    input_validation_strict: bool = Field(
        True,
        description="Enable strict input validation"
    )
    max_input_length: int = Field(
        10000,
        ge=100,
        le=1000000,
        description="Maximum input length in characters"
    )
    
    # Monitoring and Alerting
    security_monitoring_enabled: bool = Field(
        True,
        description="Enable security event monitoring"
    )
    failed_login_threshold: int = Field(
        5,
        ge=1,
        le=100,
        description="Failed login attempts before account lockout"
    )
    account_lockout_duration_minutes: int = Field(
        30,
        ge=1,
        le=1440,
        description="Account lockout duration in minutes"
    )
    suspicious_activity_threshold: int = Field(
        10,
        ge=1,
        le=1000,
        description="Threshold for suspicious activity detection"
    )
    
    # Backup and Recovery
    backup_encryption_enabled: bool = Field(
        True,
        description="Enable encryption for backups"
    )
    backup_retention_days: int = Field(
        90,
        ge=1,
        le=2555,
        description="Backup retention period in days"
    )
    
    @classmethod
    def get_config_section(cls) -> str:
        """Get the configuration section name."""
        return "security"
    
    def get_sensitive_fields(self) -> List[str]:
        """Get list of field names that contain sensitive data."""
        return [
            "session_secret_key",
            "encryption_key"
        ]
    
    @validator('session_secret_key')
    def validate_session_secret_key(cls, v: str) -> str:
        """Validate session secret key strength."""
        if len(v) < 32:
            raise ValueError("Session secret key must be at least 32 characters long")
        return v
    
    @validator('encryption_key')
    def validate_encryption_key(cls, v: Optional[str]) -> Optional[str]:
        """Validate encryption key format and strength."""
        if v is None:
            return v
        
        if len(v) < 32:
            raise ValueError("Encryption key must be at least 32 characters long")
        
        return v
    
    @validator('ip_whitelist', 'ip_blacklist')
    def validate_ip_addresses(cls, v: List[str]) -> List[str]:
        """Validate IP address formats."""
        import ipaddress
        
        validated_ips = []
        for ip in v:
            try:
                # Validate IP address or CIDR notation
                ipaddress.ip_network(ip, strict=False)
                validated_ips.append(ip)
            except ValueError:
                raise ValueError(f"Invalid IP address or CIDR notation: {ip}")
        
        return validated_ips
    
    @validator('cors_origins')
    def validate_cors_origins(cls, v: List[str]) -> List[str]:
        """Validate CORS origins format."""
        for origin in v:
            if origin != "*" and not origin.startswith(('http://', 'https://')):
                raise ValueError(f"Invalid CORS origin format: {origin}")
        return v
    
    @root_validator(skip_on_failure=True)
    def validate_rate_limits(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate rate limiting settings consistency."""
        per_minute = values.get('max_requests_per_minute', 0)
        per_hour = values.get('max_requests_per_hour', 0)
        
        if per_minute * 60 > per_hour:
            raise ValueError("Hourly rate limit must be >= (per-minute limit * 60)")
        
        return values
    
    @root_validator(skip_on_failure=True)
    def validate_token_expiry(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate token expiry settings."""
        token_expiry = values.get('token_expiry_hours', 0)
        refresh_expiry = values.get('refresh_token_expiry_days', 0)
        
        if token_expiry >= refresh_expiry * 24:
            raise ValueError("Refresh token expiry must be longer than access token expiry")
        
        return values
    
    def validate_config(self) -> None:
        """Perform additional validation after initialization."""
        # Validate encryption settings
        if self.encrypt_memories and not self.encryption_key:
            # Auto-generate encryption key if not provided
            self.encryption_key = secrets.token_urlsafe(32)
        
        # Validate compliance settings
        if self.gdpr_compliance and not self.data_deletion_enabled:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="data_deletion_enabled",
                reason="Data deletion must be enabled for GDPR compliance"
            )
    
    def validate_production_ready(self) -> None:
        """Validate that configuration is production-ready."""
        if not self.require_authentication:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="require_authentication",
                reason="Authentication must be required in production"
            )
        
        if not self.encrypt_memories:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="encrypt_memories",
                reason="Memory encryption must be enabled in production"
            )
        
        if not self.encrypt_in_transit:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="encrypt_in_transit",
                reason="TLS/SSL must be enabled in production"
            )
        
        if not self.rate_limiting_enabled:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="rate_limiting_enabled",
                reason="Rate limiting must be enabled in production"
            )
        
        if not self.audit_logging:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="audit_logging",
                reason="Audit logging must be enabled in production"
            )
        
        if "*" in self.cors_origins:
            raise InvalidConfigurationError(
                config_section=self.get_config_section(),
                config_key="cors_origins",
                reason="Wildcard CORS origins are not allowed in production"
            )
    
    def generate_api_key(self) -> str:
        """Generate a new API key."""
        return secrets.token_urlsafe(self.api_key_length)
    
    def is_ip_whitelisted(self, ip: str) -> bool:
        """Check if an IP address is whitelisted."""
        import ipaddress
        
        try:
            ip_addr = ipaddress.ip_address(ip)
            for allowed_ip in self.ip_whitelist:
                if ip_addr in ipaddress.ip_network(allowed_ip, strict=False):
                    return True
        except ValueError:
            pass
        
        return False
    
    def is_ip_blacklisted(self, ip: str) -> bool:
        """Check if an IP address is blacklisted."""
        import ipaddress
        
        try:
            ip_addr = ipaddress.ip_address(ip)
            for blocked_ip in self.ip_blacklist:
                if ip_addr in ipaddress.ip_network(blocked_ip, strict=False):
                    return True
        except ValueError:
            pass
        
        return False
