"""
API Endpoint Manager

This module provides the core functionality for managing API endpoints,
including configuration storage, health checking, credential management,
and API key rotation.
"""

import json
import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from threading import Lock
import hashlib
import secrets

from .models import (
    EndpointConfig,
    Credential,
    HealthStatus,
    HealthCheckResult,
    AuthType,
    EndpointQueryRequest,
    EndpointQueryResponse,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EndpointManager:
    """
    Manages API endpoints, credentials, and health checks.

    This class provides a centralized system for managing external API endpoints
    used by various skills. It handles configuration storage, availability checking,
    credential management, and API key rotation.

    Attributes:
        config_path: Path to the endpoint configuration file
        endpoints: Dictionary of endpoint configurations
        health_cache: Cache of recent health check results
        rate_limit_tracker: Tracks request counts for rate limiting
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        auto_load: bool = True,
        encryption_key: Optional[bytes] = None,
    ):
        """
        Initialize the endpoint manager.

        Args:
            config_path: Path to configuration file (defaults to config/endpoints.json)
            auto_load: Whether to automatically load configuration on initialization
            encryption_key: Optional encryption key for sensitive data
        """
        self.config_path = Path(config_path or "config/endpoints.json")
        self.endpoints: Dict[str, EndpointConfig] = {}
        self.health_cache: Dict[str, HealthCheckResult] = {}
        self.rate_limit_tracker: Dict[str, List[float]] = defaultdict(list)
        self._lock = Lock()
        self._encryption_key = encryption_key or self._generate_encryption_key()
        self._health_check_callbacks: List[Callable] = []

        if auto_load and self.config_path.exists():
            self.load_configuration()

    @staticmethod
    def _generate_encryption_key() -> bytes:
        """Generate a random encryption key."""
        return secrets.token_bytes(32)

    def _encrypt_value(self, value: str) -> str:
        """
        Encrypt a sensitive value.

        Note: This is a simple XOR-based encryption for demonstration.
        In production, use proper encryption libraries like cryptography.

        Args:
            value: Value to encrypt

        Returns:
            Encrypted value as hex string
        """
        if not value:
            return value

        # Simple XOR encryption (use proper crypto in production)
        key_hash = hashlib.sha256(self._encryption_key).digest()
        encrypted = bytearray()
        for i, char in enumerate(value.encode()):
            encrypted.append(char ^ key_hash[i % len(key_hash)])
        return encrypted.hex()

    def _decrypt_value(self, encrypted: str) -> str:
        """
        Decrypt an encrypted value.

        Args:
            encrypted: Encrypted value as hex string

        Returns:
            Decrypted value
        """
        if not encrypted:
            return encrypted

        try:
            key_hash = hashlib.sha256(self._encryption_key).digest()
            encrypted_bytes = bytes.fromhex(encrypted)
            decrypted = bytearray()
            for i, byte in enumerate(encrypted_bytes):
                decrypted.append(byte ^ key_hash[i % len(key_hash)])
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return encrypted

    def register_endpoint(
        self,
        name: str,
        url: str,
        credential: Optional[Credential] = None,
        **kwargs
    ) -> EndpointConfig:
        """
        Register a new API endpoint.

        Args:
            name: Unique identifier for the endpoint
            url: Base URL for the endpoint
            credential: Optional authentication credentials
            **kwargs: Additional endpoint configuration options

        Returns:
            The registered endpoint configuration

        Raises:
            ValueError: If endpoint name already exists
        """
        with self._lock:
            if name in self.endpoints:
                raise ValueError(f"Endpoint '{name}' already exists")

            config = EndpointConfig(
                name=name,
                url=url,
                credential=credential or Credential(),
                **kwargs
            )
            self.endpoints[name] = config
            logger.info(f"Registered endpoint: {name} -> {url}")
            return config

    def update_endpoint(
        self,
        name: str,
        **kwargs
    ) -> EndpointConfig:
        """
        Update an existing endpoint configuration.

        Args:
            name: Name of the endpoint to update
            **kwargs: Fields to update

        Returns:
            The updated endpoint configuration

        Raises:
            KeyError: If endpoint does not exist
        """
        with self._lock:
            if name not in self.endpoints:
                raise KeyError(f"Endpoint '{name}' not found")

            endpoint = self.endpoints[name]
            for key, value in kwargs.items():
                if hasattr(endpoint, key):
                    setattr(endpoint, key, value)

            endpoint.updated_at = datetime.utcnow()
            logger.info(f"Updated endpoint: {name}")
            return endpoint

    def delete_endpoint(self, name: str) -> None:
        """
        Delete an endpoint configuration.

        Args:
            name: Name of the endpoint to delete

        Raises:
            KeyError: If endpoint does not exist
        """
        with self._lock:
            if name not in self.endpoints:
                raise KeyError(f"Endpoint '{name}' not found")

            del self.endpoints[name]
            if name in self.health_cache:
                del self.health_cache[name]
            if name in self.rate_limit_tracker:
                del self.rate_limit_tracker[name]

            logger.info(f"Deleted endpoint: {name}")

    def get_endpoint(
        self,
        name: str,
        validate_health: bool = False
    ) -> Optional[EndpointConfig]:
        """
        Get an endpoint configuration by name.

        Args:
            name: Name of the endpoint
            validate_health: Whether to check health before returning

        Returns:
            Endpoint configuration or None if not found

        Raises:
            RuntimeError: If endpoint is unhealthy and validation is enabled
        """
        endpoint = self.endpoints.get(name)

        if endpoint is None:
            return None

        if not endpoint.enabled:
            logger.warning(f"Endpoint '{name}' is disabled")
            return None

        if validate_health:
            health = self.check_health(name)
            if not health.is_healthy():
                raise RuntimeError(
                    f"Endpoint '{name}' is unhealthy: {health.error_message}"
                )

        return endpoint

    def query_endpoint(
        self,
        request: EndpointQueryRequest
    ) -> EndpointQueryResponse:
        """
        Query an endpoint with optional health validation.

        Args:
            request: Query request parameters

        Returns:
            Query response with endpoint and health information

        Raises:
            KeyError: If endpoint not found
        """
        endpoint = self.endpoints.get(request.endpoint_name)
        if endpoint is None:
            raise KeyError(f"Endpoint '{request.endpoint_name}' not found")

        health = None
        available = endpoint.enabled

        if request.validate_health:
            health = self.check_health(request.endpoint_name)
            available = available and health.is_healthy()

        if not request.include_credentials:
            # Create a copy without credentials
            endpoint_dict = endpoint.model_dump()
            endpoint_dict['credential'] = Credential()
            endpoint = EndpointConfig(**endpoint_dict)

        return EndpointQueryResponse(
            endpoint=endpoint,
            health=health,
            available=available
        )

    def list_endpoints(
        self,
        enabled_only: bool = False,
        tags: Optional[List[str]] = None
    ) -> List[EndpointConfig]:
        """
        List all registered endpoints.

        Args:
            enabled_only: Only return enabled endpoints
            tags: Filter by tags (returns endpoints matching any tag)

        Returns:
            List of endpoint configurations
        """
        endpoints = list(self.endpoints.values())

        if enabled_only:
            endpoints = [e for e in endpoints if e.enabled]

        if tags:
            endpoints = [
                e for e in endpoints
                if any(tag in e.tags for tag in tags)
            ]

        return endpoints

    def check_health(
        self,
        name: str,
        use_cache: bool = True,
        cache_ttl: float = 60.0
    ) -> HealthCheckResult:
        """
        Check the health of an endpoint.

        Args:
            name: Name of the endpoint to check
            use_cache: Whether to use cached health results
            cache_ttl: Cache time-to-live in seconds

        Returns:
            Health check result

        Raises:
            KeyError: If endpoint not found
        """
        if name not in self.endpoints:
            raise KeyError(f"Endpoint '{name}' not found")

        # Check cache first
        if use_cache and name in self.health_cache:
            cached = self.health_cache[name]
            age = (datetime.utcnow() - cached.checked_at).total_seconds()
            if age < cache_ttl:
                return cached

        endpoint = self.endpoints[name]
        result = self._perform_health_check(endpoint)

        # Update cache
        self.health_cache[name] = result

        # Trigger callbacks
        for callback in self._health_check_callbacks:
            try:
                callback(result)
            except Exception as e:
                logger.error(f"Health check callback failed: {e}")

        return result

    def _perform_health_check(self, endpoint: EndpointConfig) -> HealthCheckResult:
        """
        Perform the actual health check.

        Args:
            endpoint: Endpoint to check

        Returns:
            Health check result
        """
        start_time = time.time()

        try:
            # Try to import requests for HTTP checks
            try:
                import requests
            except ImportError:
                # If requests not available, mark as unknown
                return HealthCheckResult(
                    endpoint_name=endpoint.name,
                    status=HealthStatus.UNKNOWN,
                    error_message="requests library not available"
                )

            url = endpoint.get_health_check_url()
            headers = endpoint.get_headers()

            response = requests.get(
                url,
                headers=headers,
                timeout=endpoint.timeout,
                params=endpoint.params
            )

            response_time = (time.time() - start_time) * 1000

            # Determine health status based on status code
            if 200 <= response.status_code < 300:
                status = HealthStatus.HEALTHY
                error_message = None
            elif 500 <= response.status_code < 600:
                status = HealthStatus.UNHEALTHY
                error_message = f"Server error: {response.status_code}"
            else:
                status = HealthStatus.DEGRADED
                error_message = f"Unexpected status: {response.status_code}"

            return HealthCheckResult(
                endpoint_name=endpoint.name,
                status=status,
                response_time_ms=response_time,
                status_code=response.status_code,
                error_message=error_message
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                endpoint_name=endpoint.name,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                error_message=str(e)
            )

    def check_all_health(
        self,
        use_cache: bool = True,
        cache_ttl: float = 60.0
    ) -> Dict[str, HealthCheckResult]:
        """
        Check health of all endpoints.

        Args:
            use_cache: Whether to use cached results
            cache_ttl: Cache time-to-live in seconds

        Returns:
            Dictionary mapping endpoint names to health results
        """
        results = {}
        for name in self.endpoints.keys():
            results[name] = self.check_health(name, use_cache, cache_ttl)
        return results

    def rotate_api_key(
        self,
        name: str,
        new_api_key: str,
        validate_before_rotation: bool = True
    ) -> bool:
        """
        Rotate the API key for an endpoint.

        Args:
            name: Name of the endpoint
            new_api_key: New API key to use
            validate_before_rotation: Test new key before rotation

        Returns:
            True if rotation successful, False otherwise

        Raises:
            KeyError: If endpoint not found
            ValueError: If endpoint doesn't use API key authentication
        """
        if name not in self.endpoints:
            raise KeyError(f"Endpoint '{name}' not found")

        endpoint = self.endpoints[name]

        if endpoint.credential.auth_type != AuthType.API_KEY:
            raise ValueError(
                f"Endpoint '{name}' does not use API key authentication"
            )

        old_key = endpoint.credential.api_key

        if validate_before_rotation:
            # Test new key
            endpoint.credential.api_key = new_api_key
            health = self.check_health(name, use_cache=False)

            if not health.is_healthy():
                # Restore old key
                endpoint.credential.api_key = old_key
                logger.error(
                    f"API key rotation failed for '{name}': "
                    f"new key validation failed"
                )
                return False

        # Update key and metadata
        endpoint.credential.api_key = new_api_key
        endpoint.credential.last_rotated = datetime.utcnow()
        endpoint.updated_at = datetime.utcnow()

        logger.info(f"Rotated API key for endpoint: {name}")
        return True

    def update_credential(
        self,
        name: str,
        credential: Credential,
        validate: bool = True
    ) -> bool:
        """
        Update credentials for an endpoint.

        Args:
            name: Name of the endpoint
            credential: New credential configuration
            validate: Whether to validate new credentials

        Returns:
            True if update successful, False otherwise

        Raises:
            KeyError: If endpoint not found
        """
        if name not in self.endpoints:
            raise KeyError(f"Endpoint '{name}' not found")

        endpoint = self.endpoints[name]
        old_credential = endpoint.credential

        if validate:
            # Test new credential
            endpoint.credential = credential
            health = self.check_health(name, use_cache=False)

            if not health.is_healthy():
                # Restore old credential
                endpoint.credential = old_credential
                logger.error(
                    f"Credential update failed for '{name}': validation failed"
                )
                return False

        # Update credential
        endpoint.credential = credential
        endpoint.credential.last_rotated = datetime.utcnow()
        endpoint.updated_at = datetime.utcnow()

        logger.info(f"Updated credentials for endpoint: {name}")
        return True

    def check_rate_limit(self, name: str) -> bool:
        """
        Check if an endpoint is within its rate limit.

        Args:
            name: Name of the endpoint

        Returns:
            True if within rate limit, False if limit exceeded

        Raises:
            KeyError: If endpoint not found
        """
        if name not in self.endpoints:
            raise KeyError(f"Endpoint '{name}' not found")

        endpoint = self.endpoints[name]

        if endpoint.rate_limit is None:
            return True

        now = time.time()
        window_start = now - 1.0  # 1 second window

        # Clean old requests
        self.rate_limit_tracker[name] = [
            t for t in self.rate_limit_tracker[name]
            if t > window_start
        ]

        # Check limit
        current_count = len(self.rate_limit_tracker[name])
        return current_count < endpoint.rate_limit

    def record_request(self, name: str) -> None:
        """
        Record a request for rate limiting purposes.

        Args:
            name: Name of the endpoint

        Raises:
            KeyError: If endpoint not found
        """
        if name not in self.endpoints:
            raise KeyError(f"Endpoint '{name}' not found")

        self.rate_limit_tracker[name].append(time.time())

    def wait_for_rate_limit(self, name: str, timeout: float = 10.0) -> bool:
        """
        Wait until rate limit allows a request.

        Args:
            name: Name of the endpoint
            timeout: Maximum time to wait in seconds

        Returns:
            True if rate limit cleared, False if timeout

        Raises:
            KeyError: If endpoint not found
        """
        start = time.time()

        while time.time() - start < timeout:
            if self.check_rate_limit(name):
                return True
            time.sleep(0.1)

        return False

    def save_configuration(self, path: Optional[Path] = None) -> None:
        """
        Save endpoint configurations to a JSON file.

        Args:
            path: Optional path to save to (defaults to config_path)
        """
        save_path = path or self.config_path
        save_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'endpoints': [
                endpoint.model_dump() for endpoint in self.endpoints.values()
            ],
            'saved_at': datetime.utcnow().isoformat()
        }

        with open(save_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        logger.info(f"Saved configuration to: {save_path}")

    def load_configuration(self, path: Optional[Path] = None) -> None:
        """
        Load endpoint configurations from a JSON file.

        Args:
            path: Optional path to load from (defaults to config_path)
        """
        load_path = path or self.config_path

        if not load_path.exists():
            logger.warning(f"Configuration file not found: {load_path}")
            return

        with open(load_path, 'r') as f:
            data = json.load(f)

        with self._lock:
            self.endpoints.clear()
            for endpoint_data in data.get('endpoints', []):
                # Convert datetime strings back to datetime objects
                if 'created_at' in endpoint_data:
                    endpoint_data['created_at'] = datetime.fromisoformat(
                        endpoint_data['created_at']
                    )
                if 'updated_at' in endpoint_data:
                    endpoint_data['updated_at'] = datetime.fromisoformat(
                        endpoint_data['updated_at']
                    )

                # Handle credential dates
                if 'credential' in endpoint_data:
                    cred = endpoint_data['credential']
                    if 'created_at' in cred:
                        cred['created_at'] = datetime.fromisoformat(
                            cred['created_at']
                        )
                    if 'last_rotated' in cred and cred['last_rotated']:
                        cred['last_rotated'] = datetime.fromisoformat(
                            cred['last_rotated']
                        )
                    if 'expires_at' in cred and cred['expires_at']:
                        cred['expires_at'] = datetime.fromisoformat(
                            cred['expires_at']
                        )

                endpoint = EndpointConfig(**endpoint_data)
                self.endpoints[endpoint.name] = endpoint

        logger.info(
            f"Loaded {len(self.endpoints)} endpoints from: {load_path}"
        )

    def add_health_check_callback(self, callback: Callable) -> None:
        """
        Add a callback to be called after each health check.

        Args:
            callback: Function that takes a HealthCheckResult parameter
        """
        self._health_check_callbacks.append(callback)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about managed endpoints.

        Returns:
            Dictionary with endpoint statistics
        """
        total = len(self.endpoints)
        enabled = sum(1 for e in self.endpoints.values() if e.enabled)
        healthy = sum(
            1 for name, health in self.health_cache.items()
            if health.is_healthy()
        )

        auth_types = defaultdict(int)
        for endpoint in self.endpoints.values():
            auth_types[endpoint.credential.auth_type.value] += 1

        return {
            'total_endpoints': total,
            'enabled_endpoints': enabled,
            'disabled_endpoints': total - enabled,
            'healthy_endpoints': healthy,
            'auth_types': dict(auth_types),
            'cache_size': len(self.health_cache),
            'last_updated': max(
                (e.updated_at for e in self.endpoints.values()),
                default=None
            )
        }

    def __repr__(self) -> str:
        """String representation of the manager."""
        return (
            f"EndpointManager("
            f"endpoints={len(self.endpoints)}, "
            f"config_path='{self.config_path}'"
            f")"
        )
