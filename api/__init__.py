"""
API Endpoint Manager Package

This package provides functionality for managing and validating API endpoints
used by various skills. It includes endpoint configuration storage, availability
checking, API key rotation, and credential management.
"""

from .endpoint_manager import EndpointManager
from .models import EndpointConfig, Credential, HealthStatus

__all__ = [
    'EndpointManager',
    'EndpointConfig',
    'Credential',
    'HealthStatus',
]

__version__ = '1.0.0'
