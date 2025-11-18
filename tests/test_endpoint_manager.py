"""
Comprehensive tests for API endpoint manager.

This module tests all functionality of the endpoint manager including:
- Endpoint registration and management
- Credential handling
- Health checking
- API key rotation
- Rate limiting
- Configuration persistence
"""

import unittest
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.endpoint_manager import EndpointManager
from api.models import (
    EndpointConfig,
    Credential,
    AuthType,
    HealthStatus,
    EndpointQueryRequest,
)


class TestEndpointManager(unittest.TestCase):
    """Test cases for EndpointManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "endpoints.json"
        self.manager = EndpointManager(
            config_path=str(self.config_path),
            auto_load=False
        )

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test endpoint manager initialization."""
        self.assertIsInstance(self.manager, EndpointManager)
        self.assertEqual(len(self.manager.endpoints), 0)
        self.assertEqual(self.config_path, self.manager.config_path)

    def test_register_endpoint(self):
        """Test registering a new endpoint."""
        endpoint = self.manager.register_endpoint(
            name="test_api",
            url="https://api.example.com",
            description="Test API endpoint"
        )

        self.assertIsInstance(endpoint, EndpointConfig)
        self.assertEqual(endpoint.name, "test_api")
        self.assertEqual(endpoint.url, "https://api.example.com")
        self.assertEqual(len(self.manager.endpoints), 1)

    def test_register_duplicate_endpoint(self):
        """Test that registering duplicate endpoint raises error."""
        self.manager.register_endpoint(
            name="test_api",
            url="https://api.example.com"
        )

        with self.assertRaises(ValueError):
            self.manager.register_endpoint(
                name="test_api",
                url="https://api2.example.com"
            )

    def test_update_endpoint(self):
        """Test updating an endpoint."""
        self.manager.register_endpoint(
            name="test_api",
            url="https://api.example.com",
            timeout=30.0
        )

        updated = self.manager.update_endpoint(
            name="test_api",
            timeout=60.0,
            description="Updated description"
        )

        self.assertEqual(updated.timeout, 60.0)
        self.assertEqual(updated.description, "Updated description")

    def test_update_nonexistent_endpoint(self):
        """Test updating non-existent endpoint raises error."""
        with self.assertRaises(KeyError):
            self.manager.update_endpoint(
                name="nonexistent",
                timeout=60.0
            )

    def test_delete_endpoint(self):
        """Test deleting an endpoint."""
        self.manager.register_endpoint(
            name="test_api",
            url="https://api.example.com"
        )

        self.assertEqual(len(self.manager.endpoints), 1)
        self.manager.delete_endpoint("test_api")
        self.assertEqual(len(self.manager.endpoints), 0)

    def test_delete_nonexistent_endpoint(self):
        """Test deleting non-existent endpoint raises error."""
        with self.assertRaises(KeyError):
            self.manager.delete_endpoint("nonexistent")

    def test_get_endpoint(self):
        """Test getting an endpoint by name."""
        self.manager.register_endpoint(
            name="test_api",
            url="https://api.example.com"
        )

        endpoint = self.manager.get_endpoint("test_api")
        self.assertIsNotNone(endpoint)
        self.assertEqual(endpoint.name, "test_api")

    def test_get_nonexistent_endpoint(self):
        """Test getting non-existent endpoint returns None."""
        endpoint = self.manager.get_endpoint("nonexistent")
        self.assertIsNone(endpoint)

    def test_get_disabled_endpoint(self):
        """Test getting disabled endpoint returns None."""
        self.manager.register_endpoint(
            name="test_api",
            url="https://api.example.com",
            enabled=False
        )

        endpoint = self.manager.get_endpoint("test_api")
        self.assertIsNone(endpoint)

    def test_list_endpoints(self):
        """Test listing all endpoints."""
        self.manager.register_endpoint(
            name="api1",
            url="https://api1.example.com"
        )
        self.manager.register_endpoint(
            name="api2",
            url="https://api2.example.com",
            enabled=False
        )

        all_endpoints = self.manager.list_endpoints()
        self.assertEqual(len(all_endpoints), 2)

        enabled_only = self.manager.list_endpoints(enabled_only=True)
        self.assertEqual(len(enabled_only), 1)
        self.assertEqual(enabled_only[0].name, "api1")

    def test_list_endpoints_by_tags(self):
        """Test filtering endpoints by tags."""
        self.manager.register_endpoint(
            name="api1",
            url="https://api1.example.com",
            tags=["production", "ml"]
        )
        self.manager.register_endpoint(
            name="api2",
            url="https://api2.example.com",
            tags=["development"]
        )

        ml_endpoints = self.manager.list_endpoints(tags=["ml"])
        self.assertEqual(len(ml_endpoints), 1)
        self.assertEqual(ml_endpoints[0].name, "api1")

    def test_credential_to_headers(self):
        """Test credential conversion to headers."""
        # API key credential
        cred_api = Credential(
            auth_type=AuthType.API_KEY,
            api_key="test-key-123"
        )
        headers = cred_api.to_headers()
        self.assertEqual(headers.get('X-API-Key'), "test-key-123")

        # Bearer token credential
        cred_bearer = Credential(
            auth_type=AuthType.BEARER_TOKEN,
            bearer_token="test-token-456"
        )
        headers = cred_bearer.to_headers()
        self.assertEqual(headers.get('Authorization'), "Bearer test-token-456")

    def test_credential_expiration(self):
        """Test credential expiration checking."""
        # Expired credential
        expired_cred = Credential(
            expires_at=datetime.utcnow() - timedelta(days=1)
        )
        self.assertTrue(expired_cred.is_expired())

        # Valid credential
        valid_cred = Credential(
            expires_at=datetime.utcnow() + timedelta(days=1)
        )
        self.assertFalse(valid_cred.is_expired())

        # No expiration
        no_expiry_cred = Credential()
        self.assertFalse(no_expiry_cred.is_expired())

    @patch('requests.get')
    def test_health_check_healthy(self, mock_get):
        """Test health check for healthy endpoint."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        self.manager.register_endpoint(
            name="test_api",
            url="https://api.example.com"
        )

        health = self.manager.check_health("test_api", use_cache=False)

        self.assertEqual(health.status, HealthStatus.HEALTHY)
        self.assertIsNotNone(health.response_time_ms)
        self.assertEqual(health.status_code, 200)
        self.assertIsNone(health.error_message)

    @patch('requests.get')
    def test_health_check_unhealthy(self, mock_get):
        """Test health check for unhealthy endpoint."""
        # Mock server error response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        self.manager.register_endpoint(
            name="test_api",
            url="https://api.example.com"
        )

        health = self.manager.check_health("test_api", use_cache=False)

        self.assertEqual(health.status, HealthStatus.UNHEALTHY)
        self.assertEqual(health.status_code, 500)
        self.assertIsNotNone(health.error_message)

    @patch('requests.get')
    def test_health_check_degraded(self, mock_get):
        """Test health check for degraded endpoint."""
        # Mock client error response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        self.manager.register_endpoint(
            name="test_api",
            url="https://api.example.com"
        )

        health = self.manager.check_health("test_api", use_cache=False)

        self.assertEqual(health.status, HealthStatus.DEGRADED)
        self.assertEqual(health.status_code, 401)

    @patch('requests.get')
    def test_health_check_exception(self, mock_get):
        """Test health check when request raises exception."""
        # Mock request exception
        mock_get.side_effect = Exception("Connection failed")

        self.manager.register_endpoint(
            name="test_api",
            url="https://api.example.com"
        )

        health = self.manager.check_health("test_api", use_cache=False)

        self.assertEqual(health.status, HealthStatus.UNHEALTHY)
        self.assertIn("Connection failed", health.error_message)

    @patch('requests.get')
    def test_health_check_caching(self, mock_get):
        """Test health check result caching."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        self.manager.register_endpoint(
            name="test_api",
            url="https://api.example.com"
        )

        # First call
        health1 = self.manager.check_health("test_api", use_cache=True)
        self.assertEqual(mock_get.call_count, 1)

        # Second call should use cache
        health2 = self.manager.check_health("test_api", use_cache=True)
        self.assertEqual(mock_get.call_count, 1)  # No additional call

        # Results should be the same
        self.assertEqual(health1.checked_at, health2.checked_at)

    @patch('requests.get')
    def test_check_all_health(self, mock_get):
        """Test checking health of all endpoints."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        self.manager.register_endpoint(
            name="api1",
            url="https://api1.example.com"
        )
        self.manager.register_endpoint(
            name="api2",
            url="https://api2.example.com"
        )

        results = self.manager.check_all_health(use_cache=False)

        self.assertEqual(len(results), 2)
        self.assertIn("api1", results)
        self.assertIn("api2", results)
        self.assertEqual(results["api1"].status, HealthStatus.HEALTHY)
        self.assertEqual(results["api2"].status, HealthStatus.HEALTHY)

    @patch('requests.get')
    def test_rotate_api_key_success(self, mock_get):
        """Test successful API key rotation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        credential = Credential(
            auth_type=AuthType.API_KEY,
            api_key="old-key"
        )

        self.manager.register_endpoint(
            name="test_api",
            url="https://api.example.com",
            credential=credential
        )

        success = self.manager.rotate_api_key(
            "test_api",
            "new-key",
            validate_before_rotation=True
        )

        self.assertTrue(success)
        endpoint = self.manager.get_endpoint("test_api")
        self.assertEqual(endpoint.credential.api_key, "new-key")
        self.assertIsNotNone(endpoint.credential.last_rotated)

    @patch('requests.get')
    def test_rotate_api_key_validation_failure(self, mock_get):
        """Test API key rotation with validation failure."""
        mock_response = Mock()
        mock_response.status_code = 401  # Unauthorized
        mock_get.return_value = mock_response

        credential = Credential(
            auth_type=AuthType.API_KEY,
            api_key="old-key"
        )

        self.manager.register_endpoint(
            name="test_api",
            url="https://api.example.com",
            credential=credential
        )

        success = self.manager.rotate_api_key(
            "test_api",
            "invalid-key",
            validate_before_rotation=True
        )

        self.assertFalse(success)
        endpoint = self.manager.get_endpoint("test_api")
        # Should still have old key
        self.assertEqual(endpoint.credential.api_key, "old-key")

    def test_rotate_api_key_wrong_auth_type(self):
        """Test API key rotation with wrong auth type."""
        credential = Credential(
            auth_type=AuthType.BEARER_TOKEN,
            bearer_token="token"
        )

        self.manager.register_endpoint(
            name="test_api",
            url="https://api.example.com",
            credential=credential
        )

        with self.assertRaises(ValueError):
            self.manager.rotate_api_key("test_api", "new-key")

    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        self.manager.register_endpoint(
            name="test_api",
            url="https://api.example.com",
            rate_limit=5.0  # 5 requests per second
        )

        # Should allow first 5 requests
        for i in range(5):
            self.assertTrue(self.manager.check_rate_limit("test_api"))
            self.manager.record_request("test_api")

        # 6th request should be blocked
        self.assertFalse(self.manager.check_rate_limit("test_api"))

    def test_no_rate_limit(self):
        """Test endpoint without rate limit."""
        self.manager.register_endpoint(
            name="test_api",
            url="https://api.example.com",
            rate_limit=None  # No limit
        )

        # Should allow unlimited requests
        for i in range(100):
            self.assertTrue(self.manager.check_rate_limit("test_api"))
            self.manager.record_request("test_api")

    def test_save_and_load_configuration(self):
        """Test saving and loading configuration."""
        # Create some endpoints
        self.manager.register_endpoint(
            name="api1",
            url="https://api1.example.com",
            description="First API"
        )

        credential = Credential(
            auth_type=AuthType.API_KEY,
            api_key="test-key"
        )
        self.manager.register_endpoint(
            name="api2",
            url="https://api2.example.com",
            credential=credential,
            tags=["production"]
        )

        # Save configuration
        self.manager.save_configuration()
        self.assertTrue(self.config_path.exists())

        # Create new manager and load
        new_manager = EndpointManager(
            config_path=str(self.config_path),
            auto_load=True
        )

        self.assertEqual(len(new_manager.endpoints), 2)
        self.assertIn("api1", new_manager.endpoints)
        self.assertIn("api2", new_manager.endpoints)

        api2 = new_manager.endpoints["api2"]
        self.assertEqual(api2.credential.auth_type, AuthType.API_KEY)
        self.assertEqual(api2.tags, ["production"])

    def test_query_endpoint(self):
        """Test querying an endpoint."""
        self.manager.register_endpoint(
            name="test_api",
            url="https://api.example.com"
        )

        request = EndpointQueryRequest(
            endpoint_name="test_api",
            include_credentials=True,
            validate_health=False
        )

        response = self.manager.query_endpoint(request)

        self.assertIsNotNone(response.endpoint)
        self.assertEqual(response.endpoint.name, "test_api")
        self.assertTrue(response.available)

    def test_query_endpoint_without_credentials(self):
        """Test querying endpoint without credentials."""
        credential = Credential(
            auth_type=AuthType.API_KEY,
            api_key="secret-key"
        )

        self.manager.register_endpoint(
            name="test_api",
            url="https://api.example.com",
            credential=credential
        )

        request = EndpointQueryRequest(
            endpoint_name="test_api",
            include_credentials=False
        )

        response = self.manager.query_endpoint(request)

        # Credential should be empty
        self.assertEqual(response.endpoint.credential.auth_type, AuthType.NONE)
        self.assertIsNone(response.endpoint.credential.api_key)

    def test_get_statistics(self):
        """Test getting endpoint statistics."""
        self.manager.register_endpoint(
            name="api1",
            url="https://api1.example.com",
            credential=Credential(auth_type=AuthType.API_KEY, api_key="key1")
        )
        self.manager.register_endpoint(
            name="api2",
            url="https://api2.example.com",
            enabled=False,
            credential=Credential(auth_type=AuthType.BEARER_TOKEN, bearer_token="token")
        )

        stats = self.manager.get_statistics()

        self.assertEqual(stats['total_endpoints'], 2)
        self.assertEqual(stats['enabled_endpoints'], 1)
        self.assertEqual(stats['disabled_endpoints'], 1)
        self.assertEqual(stats['auth_types']['api_key'], 1)
        self.assertEqual(stats['auth_types']['bearer_token'], 1)

    def test_health_check_callback(self):
        """Test health check callbacks."""
        callback_results = []

        def callback(result):
            callback_results.append(result)

        self.manager.add_health_check_callback(callback)

        self.manager.register_endpoint(
            name="test_api",
            url="https://api.example.com"
        )

        # Trigger health check (will fail without requests library or mock)
        self.manager.check_health("test_api", use_cache=False)

        # Callback should have been called
        self.assertEqual(len(callback_results), 1)

    def test_encryption_decryption(self):
        """Test value encryption and decryption."""
        original = "secret-api-key-12345"

        encrypted = self.manager._encrypt_value(original)
        self.assertNotEqual(encrypted, original)

        decrypted = self.manager._decrypt_value(encrypted)
        self.assertEqual(decrypted, original)

    def test_endpoint_config_validation(self):
        """Test endpoint configuration validation."""
        # Valid URL
        config = EndpointConfig(
            name="test",
            url="https://api.example.com"
        )
        self.assertEqual(config.url, "https://api.example.com")

        # Invalid URL should raise error
        with self.assertRaises(ValueError):
            EndpointConfig(
                name="test",
                url="invalid-url"
            )

    def test_concurrent_access(self):
        """Test thread-safe concurrent access."""
        import threading

        def add_endpoint(i):
            self.manager.register_endpoint(
                name=f"api_{i}",
                url=f"https://api{i}.example.com"
            )

        threads = []
        for i in range(10):
            thread = threading.Thread(target=add_endpoint, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.assertEqual(len(self.manager.endpoints), 10)


class TestEndpointConfig(unittest.TestCase):
    """Test cases for EndpointConfig model."""

    def test_default_values(self):
        """Test default configuration values."""
        config = EndpointConfig(
            name="test",
            url="https://api.example.com"
        )

        self.assertTrue(config.enabled)
        self.assertEqual(config.timeout, 30.0)
        self.assertEqual(config.max_retries, 3)
        self.assertEqual(config.retry_delay, 1.0)
        self.assertEqual(len(config.tags), 0)

    def test_get_health_check_url(self):
        """Test getting health check URL."""
        # With custom health check URL
        config = EndpointConfig(
            name="test",
            url="https://api.example.com",
            health_check_url="https://api.example.com/health"
        )
        self.assertEqual(
            config.get_health_check_url(),
            "https://api.example.com/health"
        )

        # Without custom health check URL
        config2 = EndpointConfig(
            name="test",
            url="https://api.example.com"
        )
        self.assertEqual(
            config2.get_health_check_url(),
            "https://api.example.com"
        )

    def test_get_headers(self):
        """Test getting combined headers."""
        credential = Credential(
            auth_type=AuthType.API_KEY,
            api_key="test-key"
        )

        config = EndpointConfig(
            name="test",
            url="https://api.example.com",
            headers={"User-Agent": "TestClient/1.0"},
            credential=credential
        )

        headers = config.get_headers()
        self.assertEqual(headers.get("User-Agent"), "TestClient/1.0")
        self.assertEqual(headers.get("X-API-Key"), "test-key")


if __name__ == '__main__':
    unittest.main()
