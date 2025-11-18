"""
Data models for API endpoint management.

This module defines Pydantic models for endpoint configurations, credentials,
and health status tracking.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator, HttpUrl


class AuthType(str, Enum):
    """Authentication types supported by the endpoint manager."""
    NONE = "none"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    OAUTH2 = "oauth2"
    CUSTOM = "custom"


class HealthStatus(str, Enum):
    """Health status of an endpoint."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class Credential(BaseModel):
    """
    Credential information for API authentication.

    Attributes:
        auth_type: Type of authentication mechanism
        api_key: API key for authentication (encrypted at rest)
        bearer_token: Bearer token for authentication
        username: Username for basic auth
        password: Password for basic auth (encrypted at rest)
        custom_headers: Custom headers for authentication
        metadata: Additional metadata for the credential
        expires_at: Optional expiration timestamp
        created_at: Timestamp when credential was created
        last_rotated: Timestamp when credential was last rotated
    """
    auth_type: AuthType = Field(default=AuthType.NONE)
    api_key: Optional[str] = Field(default=None, repr=False)
    bearer_token: Optional[str] = Field(default=None, repr=False)
    username: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None, repr=False)
    custom_headers: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_rotated: Optional[datetime] = None

    @validator('api_key', 'bearer_token', 'password')
    def validate_sensitive_fields(cls, v):
        """Validate that sensitive fields are not empty strings."""
        if v is not None and v == "":
            return None
        return v

    def is_expired(self) -> bool:
        """Check if the credential is expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def to_headers(self) -> Dict[str, str]:
        """
        Convert credential to HTTP headers.

        Returns:
            Dictionary of HTTP headers for authentication

        Raises:
            ValueError: If required fields are missing for the auth type
        """
        headers = dict(self.custom_headers)

        if self.auth_type == AuthType.API_KEY:
            if self.api_key:
                headers['X-API-Key'] = self.api_key
            else:
                raise ValueError("API key is required for API_KEY authentication")

        elif self.auth_type == AuthType.BEARER_TOKEN:
            if self.bearer_token:
                headers['Authorization'] = f'Bearer {self.bearer_token}'
            else:
                raise ValueError("Bearer token is required for BEARER_TOKEN authentication")

        elif self.auth_type == AuthType.BASIC_AUTH:
            if self.username and self.password:
                import base64
                credentials = f"{self.username}:{self.password}"
                encoded = base64.b64encode(credentials.encode()).decode()
                headers['Authorization'] = f'Basic {encoded}'
            else:
                raise ValueError("Username and password are required for BASIC_AUTH authentication")

        elif self.auth_type == AuthType.OAUTH2:
            # OAuth2 typically uses bearer tokens
            if self.bearer_token:
                headers['Authorization'] = f'Bearer {self.bearer_token}'
            else:
                raise ValueError("Bearer token is required for OAUTH2 authentication")

        elif self.auth_type == AuthType.CUSTOM:
            # Custom auth relies entirely on custom_headers
            if not self.custom_headers:
                raise ValueError("Custom headers are required for CUSTOM authentication")

        # AuthType.NONE requires no additional headers

        return headers

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EndpointConfig(BaseModel):
    """
    Configuration for an API endpoint.

    Attributes:
        name: Unique identifier for the endpoint
        url: Base URL for the endpoint
        description: Human-readable description
        credential: Authentication credentials
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        headers: Default headers to include in requests
        params: Default query parameters
        enabled: Whether the endpoint is enabled
        rate_limit: Maximum requests per second (None for unlimited)
        health_check_url: URL for health checks (defaults to base URL)
        health_check_interval: Seconds between health checks
        tags: Tags for categorizing endpoints
        metadata: Additional metadata
        created_at: Timestamp when endpoint was created
        updated_at: Timestamp when endpoint was last updated
    """
    name: str = Field(..., min_length=1)
    url: str = Field(...)
    description: Optional[str] = None
    credential: Credential = Field(default_factory=Credential)
    timeout: float = Field(default=30.0, gt=0)
    max_retries: int = Field(default=3, ge=0)
    retry_delay: float = Field(default=1.0, ge=0)
    headers: Dict[str, str] = Field(default_factory=dict)
    params: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = Field(default=True)
    rate_limit: Optional[float] = Field(default=None, gt=0)
    health_check_url: Optional[str] = None
    health_check_interval: float = Field(default=60.0, gt=0)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('url', 'health_check_url')
    def validate_url(cls, v):
        """Validate URL format."""
        if v is None:
            return v
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

    def get_health_check_url(self) -> str:
        """Get the URL to use for health checks."""
        return self.health_check_url or self.url

    def get_headers(self) -> Dict[str, str]:
        """Get all headers including credential headers."""
        headers = dict(self.headers)
        headers.update(self.credential.to_headers())
        return headers

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HealthCheckResult(BaseModel):
    """
    Result of a health check operation.

    Attributes:
        endpoint_name: Name of the endpoint checked
        status: Health status
        response_time_ms: Response time in milliseconds
        status_code: HTTP status code received
        error_message: Error message if check failed
        checked_at: Timestamp of the check
        metadata: Additional metadata from the check
    """
    endpoint_name: str
    status: HealthStatus
    response_time_ms: Optional[float] = None
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    checked_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def is_healthy(self) -> bool:
        """Check if the endpoint is healthy."""
        return self.status == HealthStatus.HEALTHY

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EndpointQueryRequest(BaseModel):
    """
    Request for querying an endpoint.

    Attributes:
        endpoint_name: Name of the endpoint to query
        include_credentials: Whether to include credentials in response
        validate_health: Whether to validate health before returning
    """
    endpoint_name: str
    include_credentials: bool = Field(default=True)
    validate_health: bool = Field(default=False)


class EndpointQueryResponse(BaseModel):
    """
    Response from querying an endpoint.

    Attributes:
        endpoint: The endpoint configuration
        health: Current health status (if requested)
        available: Whether the endpoint is available for use
    """
    endpoint: EndpointConfig
    health: Optional[HealthCheckResult] = None
    available: bool = Field(default=True)
