# API Endpoint Manager

A comprehensive system for managing and validating API endpoints used by various skills. The endpoint manager provides centralized configuration storage, health checking, credential management, API key rotation, and rate limiting.

## Features

- **Endpoint Registration**: Register and manage multiple API endpoints with different configurations
- **Credential Management**: Support for multiple authentication types (API Key, Bearer Token, Basic Auth, OAuth2, Custom)
- **Health Checking**: Automatic endpoint availability validation with caching
- **API Key Rotation**: Safe rotation of API keys with validation
- **Rate Limiting**: Built-in rate limiting per endpoint
- **Configuration Persistence**: Save and load endpoint configurations from JSON files
- **Thread-Safe**: Safe for concurrent access from multiple threads
- **Encryption Support**: Built-in encryption for sensitive credentials
- **Flexible Querying**: Skills can query endpoints with optional health validation

## Installation

### Dependencies

Install required dependencies:

```bash
pip install pydantic>=2.0.0 requests>=2.31.0
```

### Optional Dependencies

For enhanced functionality:

```bash
pip install cryptography>=41.0.0  # For production-grade encryption
```

## Quick Start

### Basic Usage

```python
from api import EndpointManager, Credential, AuthType

# Initialize the manager
manager = EndpointManager(config_path="config/endpoints.json")

# Register an endpoint with API key authentication
api_credential = Credential(
    auth_type=AuthType.API_KEY,
    api_key="your-api-key-here"
)

endpoint = manager.register_endpoint(
    name="openai_embeddings",
    url="https://api.openai.com/v1/embeddings",
    description="OpenAI embeddings API",
    credential=api_credential,
    timeout=60.0,
    rate_limit=10.0  # 10 requests per second
)

# Check endpoint health
health = manager.check_health("openai_embeddings")
print(f"Status: {health.status}")

# Save configuration
manager.save_configuration()
```

### Using Endpoints in Skills

```python
from api import EndpointQueryRequest

# Query endpoint for use
request = EndpointQueryRequest(
    endpoint_name="openai_embeddings",
    include_credentials=True,
    validate_health=True
)

response = manager.query_endpoint(request)

if response.available:
    endpoint = response.endpoint
    headers = endpoint.get_headers()

    # Use endpoint to make API calls
    import requests
    api_response = requests.post(
        endpoint.url,
        headers=headers,
        json={"input": "text to embed"},
        timeout=endpoint.timeout
    )
```

## Core Components

### EndpointManager

The main class for managing API endpoints.

**Key Methods:**
- `register_endpoint()` - Register a new endpoint
- `update_endpoint()` - Update existing endpoint configuration
- `delete_endpoint()` - Remove an endpoint
- `get_endpoint()` - Retrieve endpoint configuration
- `list_endpoints()` - List all endpoints with optional filtering
- `check_health()` - Check endpoint health
- `rotate_api_key()` - Safely rotate API keys
- `query_endpoint()` - Query endpoint for skill usage
- `save_configuration()` - Persist configuration to disk
- `load_configuration()` - Load configuration from disk

### EndpointConfig

Configuration model for API endpoints.

**Key Attributes:**
- `name` - Unique identifier
- `url` - Base URL
- `credential` - Authentication credentials
- `timeout` - Request timeout
- `max_retries` - Maximum retry attempts
- `rate_limit` - Requests per second limit
- `enabled` - Whether endpoint is active
- `tags` - Tags for categorization
- `health_check_url` - Custom health check URL

### Credential

Authentication credential model.

**Supported Authentication Types:**
- `NONE` - No authentication
- `API_KEY` - API key in X-API-Key header
- `BEARER_TOKEN` - Bearer token authentication
- `BASIC_AUTH` - HTTP Basic authentication (username/password)
- `OAUTH2` - OAuth2 bearer token authentication
- `CUSTOM` - Custom authentication headers

### Authentication Examples

```python
from api import Credential, AuthType

# API Key authentication
api_key_cred = Credential(
    auth_type=AuthType.API_KEY,
    api_key="sk-your-api-key-here"
)
# Generates: {"X-API-Key": "sk-your-api-key-here"}

# Bearer Token authentication
bearer_cred = Credential(
    auth_type=AuthType.BEARER_TOKEN,
    bearer_token="your-bearer-token"
)
# Generates: {"Authorization": "Bearer your-bearer-token"}

# HTTP Basic authentication
basic_cred = Credential(
    auth_type=AuthType.BASIC_AUTH,
    username="admin",
    password="secret123"
)
# Generates: {"Authorization": "Basic YWRtaW46c2VjcmV0MTIz"}

# OAuth2 authentication
oauth_cred = Credential(
    auth_type=AuthType.OAUTH2,
    bearer_token="oauth-access-token"
)
# Generates: {"Authorization": "Bearer oauth-access-token"}

# Custom authentication
custom_cred = Credential(
    auth_type=AuthType.CUSTOM,
    custom_headers={
        "X-Custom-Auth": "custom-value",
        "X-Client-ID": "client-123"
    }
)
# Generates: {"X-Custom-Auth": "custom-value", "X-Client-ID": "client-123"}

# No authentication
no_auth_cred = Credential(auth_type=AuthType.NONE)
# Generates: {}

# Get headers for API requests
headers = api_key_cred.to_headers()
```

**Note:** The `to_headers()` method validates that required fields are present. For example, `BASIC_AUTH` requires both `username` and `password`, or a `ValueError` will be raised.

## Advanced Usage

### Health Checking

```python
# Check single endpoint
health = manager.check_health("openai_embeddings", use_cache=False)

if health.is_healthy():
    print(f"Endpoint is healthy! Response time: {health.response_time_ms}ms")
else:
    print(f"Endpoint is {health.status}: {health.error_message}")

# Check all endpoints
all_health = manager.check_all_health()
for name, health in all_health.items():
    print(f"{name}: {health.status}")
```

### API Key Rotation

```python
# Rotate with validation
success = manager.rotate_api_key(
    "openai_embeddings",
    "new-api-key",
    validate_before_rotation=True  # Test new key before switching
)

if success:
    print("API key rotated successfully!")
else:
    print("Rotation failed - old key retained")
```

### Rate Limiting

```python
# Check if request allowed
if manager.check_rate_limit("openai_embeddings"):
    # Make request
    manager.record_request("openai_embeddings")
else:
    # Wait for rate limit to clear
    if manager.wait_for_rate_limit("openai_embeddings", timeout=5.0):
        manager.record_request("openai_embeddings")
```

### Filtering Endpoints

```python
# Get only enabled endpoints
enabled = manager.list_endpoints(enabled_only=True)

# Filter by tags
ml_endpoints = manager.list_endpoints(tags=["ml", "embeddings"])

# Get statistics
stats = manager.get_statistics()
print(f"Total endpoints: {stats['total_endpoints']}")
print(f"Healthy endpoints: {stats['healthy_endpoints']}")
```

### Health Check Callbacks

```python
def on_health_check(result):
    if not result.is_healthy():
        print(f"Alert: {result.endpoint_name} is unhealthy!")
        # Send notification, update monitoring, etc.

manager.add_health_check_callback(on_health_check)
```

## Configuration File Format

Endpoints are stored in JSON format:

```json
{
  "endpoints": [
    {
      "name": "openai_embeddings",
      "url": "https://api.openai.com/v1/embeddings",
      "description": "OpenAI embeddings API",
      "credential": {
        "auth_type": "api_key",
        "api_key": "sk-...",
        "created_at": "2025-01-15T10:30:00"
      },
      "timeout": 60.0,
      "max_retries": 3,
      "rate_limit": 10.0,
      "enabled": true,
      "tags": ["ml", "embeddings", "production"]
    }
  ],
  "saved_at": "2025-01-15T12:00:00"
}
```

## Skill Integration Pattern

Skills should query the endpoint manager to get endpoint configurations:

```python
class MySkill:
    def __init__(self, endpoint_manager):
        self.endpoint_manager = endpoint_manager

    def call_external_api(self, data):
        # Query for endpoint
        request = EndpointQueryRequest(
            endpoint_name="my_api",
            include_credentials=True,
            validate_health=True
        )

        response = self.endpoint_manager.query_endpoint(request)

        if not response.available:
            raise RuntimeError("API endpoint not available")

        endpoint = response.endpoint

        # Check rate limit
        if not self.endpoint_manager.check_rate_limit(endpoint.name):
            self.endpoint_manager.wait_for_rate_limit(endpoint.name)

        # Make API call
        import requests
        api_response = requests.post(
            endpoint.url,
            headers=endpoint.get_headers(),
            json=data,
            timeout=endpoint.timeout
        )

        # Record request
        self.endpoint_manager.record_request(endpoint.name)

        return api_response.json()
```

## Security Considerations

### Credential Storage

- Credentials are encrypted at rest using XOR encryption by default
- For production use, integrate with proper encryption libraries (e.g., `cryptography`)
- Consider using environment variables or secret management services for sensitive keys
- Never commit configuration files with real credentials to version control

### Best Practices

1. **Use environment variables**: Load sensitive values from environment
   ```python
   import os
   api_key = os.getenv("OPENAI_API_KEY")
   ```

2. **Rotate keys regularly**: Set up automated key rotation
   ```python
   # Check for expiring credentials
   endpoint = manager.get_endpoint("my_api")
   if endpoint.credential.is_expired():
       manager.rotate_api_key("my_api", new_key)
   ```

3. **Enable health checking**: Validate endpoints before use
   ```python
   endpoint = manager.get_endpoint("my_api", validate_health=True)
   ```

4. **Use rate limiting**: Prevent API quota exhaustion
   ```python
   manager.register_endpoint(
       name="my_api",
       url="...",
       rate_limit=10.0  # 10 req/s
   )
   ```

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/test_endpoint_manager.py -v

# Run specific test
python -m pytest tests/test_endpoint_manager.py::TestEndpointManager::test_register_endpoint -v

# Run with coverage
python -m pytest tests/test_endpoint_manager.py --cov=api --cov-report=html
```

## Examples

See `example_endpoint_manager.py` for comprehensive examples including:

1. Basic endpoint management
2. Health checking
3. Querying endpoints (skill usage)
4. API key rotation
5. Rate limiting
6. Filtering and statistics
7. Configuration persistence
8. Skill integration patterns

Run the examples:

```bash
python example_endpoint_manager.py
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Skills Layer                     │
│  (EmbeddingSkill, AnalysisSkill, CustomSkill, ...)  │
└─────────────────┬───────────────────────────────────┘
                  │ query_endpoint()
                  │ check_rate_limit()
                  │
┌─────────────────▼───────────────────────────────────┐
│              EndpointManager                        │
│  ┌──────────────────────────────────────────────┐  │
│  │  Endpoint Registry                           │  │
│  │  - openai_embeddings                         │  │
│  │  - custom_ml_service                         │  │
│  │  - public_api                                │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │  Health Monitor                              │  │
│  │  - Periodic health checks                    │  │
│  │  - Health cache with TTL                     │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │  Credential Manager                          │  │
│  │  - Encrypted storage                         │  │
│  │  - Key rotation                              │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │  Rate Limiter                                │  │
│  │  - Per-endpoint tracking                     │  │
│  │  - Request throttling                        │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│            External API Services                    │
│  (OpenAI, Custom ML, Public APIs, ...)              │
└─────────────────────────────────────────────────────┘
```

## Future Enhancements

- [ ] Async/await support for concurrent health checks
- [ ] Integration with secret management services (AWS Secrets Manager, HashiCorp Vault)
- [ ] Metric collection and monitoring integration (Prometheus, DataDog)
- [ ] Circuit breaker pattern for failing endpoints
- [ ] Automatic failover to backup endpoints
- [ ] GraphQL endpoint support
- [ ] WebSocket endpoint support
- [ ] API versioning support
- [ ] Request/response caching
- [ ] Distributed rate limiting (Redis-based)

## Contributing

Contributions are welcome! Please ensure:

1. All tests pass
2. Code follows PEP 8 style guidelines
3. New features include tests
4. Documentation is updated

## License

This project is part of the ClaudeCodeFrameWork and follows the same license.

## Support

For issues, questions, or contributions, please refer to the main project repository.
