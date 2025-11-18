"""
Example usage of the API Endpoint Manager.

This example demonstrates how to:
1. Initialize the endpoint manager
2. Register API endpoints with different authentication types
3. Check endpoint health
4. Rotate API keys
5. Query endpoints for use by skills
6. Manage rate limiting
7. Save and load configurations
"""

from datetime import datetime, timedelta
from api import EndpointManager, EndpointConfig, Credential, AuthType, EndpointQueryRequest


def example_basic_usage():
    """Basic usage example."""
    print("=" * 60)
    print("Example 1: Basic Endpoint Management")
    print("=" * 60)

    # Initialize the manager
    manager = EndpointManager(config_path="config/endpoints.json", auto_load=False)

    # Register a simple endpoint without authentication
    endpoint1 = manager.register_endpoint(
        name="public_api",
        url="https://api.publicapis.org/entries",
        description="Public APIs directory",
        tags=["public", "free"]
    )
    print(f"\n✓ Registered endpoint: {endpoint1.name}")

    # Register an endpoint with API key authentication
    api_key_credential = Credential(
        auth_type=AuthType.API_KEY,
        api_key="your-api-key-here",
        metadata={"provider": "openai"}
    )

    endpoint2 = manager.register_endpoint(
        name="openai_embeddings",
        url="https://api.openai.com/v1/embeddings",
        description="OpenAI embeddings API",
        credential=api_key_credential,
        timeout=60.0,
        max_retries=3,
        tags=["ml", "embeddings", "production"]
    )
    print(f"✓ Registered endpoint: {endpoint2.name}")

    # Register an endpoint with bearer token
    bearer_credential = Credential(
        auth_type=AuthType.BEARER_TOKEN,
        bearer_token="your-bearer-token",
        expires_at=datetime.utcnow() + timedelta(days=30)
    )

    endpoint3 = manager.register_endpoint(
        name="custom_ml_service",
        url="https://ml.example.com/api/v1",
        description="Custom ML inference service",
        credential=bearer_credential,
        rate_limit=10.0,  # 10 requests per second
        tags=["ml", "custom"]
    )
    print(f"✓ Registered endpoint: {endpoint3.name}")

    # List all endpoints
    print(f"\n📋 Total endpoints registered: {len(manager.list_endpoints())}")

    return manager


def example_health_checking(manager: EndpointManager):
    """Health checking example."""
    print("\n" + "=" * 60)
    print("Example 2: Health Checking")
    print("=" * 60)

    # Check health of a specific endpoint
    print("\n🔍 Checking health of individual endpoints...")

    for endpoint_name in manager.endpoints.keys():
        health = manager.check_health(endpoint_name, use_cache=False)
        status_emoji = "✅" if health.is_healthy() else "❌"

        print(f"\n{status_emoji} {endpoint_name}:")
        print(f"   Status: {health.status.value}")
        if health.response_time_ms:
            print(f"   Response time: {health.response_time_ms:.2f}ms")
        if health.error_message:
            print(f"   Error: {health.error_message}")

    # Check all endpoints at once
    print("\n🔍 Checking all endpoints...")
    all_health = manager.check_all_health(use_cache=False)

    healthy_count = sum(1 for h in all_health.values() if h.is_healthy())
    print(f"\n📊 Health Summary: {healthy_count}/{len(all_health)} endpoints healthy")


def example_querying_endpoints(manager: EndpointManager):
    """Example of querying endpoints (how skills would use it)."""
    print("\n" + "=" * 60)
    print("Example 3: Querying Endpoints (Skill Usage)")
    print("=" * 60)

    # Skill needs to call an embedding API
    print("\n🔧 Skill requesting embedding endpoint...")

    request = EndpointQueryRequest(
        endpoint_name="openai_embeddings",
        include_credentials=True,
        validate_health=False  # Set to True to ensure endpoint is healthy
    )

    try:
        response = manager.query_endpoint(request)

        if response.available:
            endpoint = response.endpoint
            print(f"✅ Endpoint available!")
            print(f"   URL: {endpoint.url}")
            print(f"   Auth type: {endpoint.credential.auth_type.value}")
            print(f"   Timeout: {endpoint.timeout}s")

            # Get headers for making requests
            headers = endpoint.get_headers()
            print(f"   Headers: {list(headers.keys())}")

            # Skill would now use this endpoint to make API calls
            print("\n📡 Skill can now make API calls using this configuration")

        else:
            print("❌ Endpoint not available")

    except KeyError as e:
        print(f"❌ Error: {e}")


def example_api_key_rotation(manager: EndpointManager):
    """API key rotation example."""
    print("\n" + "=" * 60)
    print("Example 4: API Key Rotation")
    print("=" * 60)

    endpoint_name = "openai_embeddings"

    # Show current key info
    endpoint = manager.get_endpoint(endpoint_name)
    print(f"\n🔑 Current API key for '{endpoint_name}':")
    print(f"   Created: {endpoint.credential.created_at}")
    if endpoint.credential.last_rotated:
        print(f"   Last rotated: {endpoint.credential.last_rotated}")
    else:
        print(f"   Last rotated: Never")

    # Rotate API key (with validation)
    print(f"\n🔄 Rotating API key...")
    new_api_key = "new-api-key-here"

    # Note: This will validate the new key by making a health check
    # In production, this would ensure the new key works before switching
    success = manager.rotate_api_key(
        endpoint_name,
        new_api_key,
        validate_before_rotation=False  # Set True in production
    )

    if success:
        print(f"✅ API key rotated successfully!")
        endpoint = manager.get_endpoint(endpoint_name)
        print(f"   New rotation time: {endpoint.credential.last_rotated}")
    else:
        print(f"❌ API key rotation failed (new key validation failed)")


def example_rate_limiting(manager: EndpointManager):
    """Rate limiting example."""
    print("\n" + "=" * 60)
    print("Example 5: Rate Limiting")
    print("=" * 60)

    endpoint_name = "custom_ml_service"
    endpoint = manager.get_endpoint(endpoint_name)

    print(f"\n⏱️  Rate limit for '{endpoint_name}': {endpoint.rate_limit} req/s")

    # Simulate making requests
    print(f"\n🚀 Simulating API requests...")

    for i in range(12):
        if manager.check_rate_limit(endpoint_name):
            print(f"   Request {i+1}: ✅ Allowed")
            manager.record_request(endpoint_name)
        else:
            print(f"   Request {i+1}: ❌ Rate limit exceeded")

            # Wait for rate limit to clear
            print(f"   ⏳ Waiting for rate limit...")
            if manager.wait_for_rate_limit(endpoint_name, timeout=2.0):
                print(f"   ✅ Rate limit cleared")
                manager.record_request(endpoint_name)
            else:
                print(f"   ❌ Timeout waiting for rate limit")


def example_filtering_and_statistics(manager: EndpointManager):
    """Filtering and statistics example."""
    print("\n" + "=" * 60)
    print("Example 6: Filtering and Statistics")
    print("=" * 60)

    # Filter by tags
    print("\n🏷️  ML-related endpoints:")
    ml_endpoints = manager.list_endpoints(tags=["ml"])
    for ep in ml_endpoints:
        print(f"   - {ep.name}: {ep.url}")

    # Get statistics
    print("\n📊 Endpoint Statistics:")
    stats = manager.get_statistics()

    print(f"   Total endpoints: {stats['total_endpoints']}")
    print(f"   Enabled: {stats['enabled_endpoints']}")
    print(f"   Disabled: {stats['disabled_endpoints']}")

    print(f"\n   Authentication types:")
    for auth_type, count in stats['auth_types'].items():
        print(f"      {auth_type}: {count}")


def example_persistence(manager: EndpointManager):
    """Configuration persistence example."""
    print("\n" + "=" * 60)
    print("Example 7: Saving and Loading Configuration")
    print("=" * 60)

    # Save configuration
    print("\n💾 Saving configuration to disk...")
    manager.save_configuration()
    print(f"   ✅ Saved to: {manager.config_path}")

    # Load configuration in a new manager
    print(f"\n📂 Loading configuration in new manager...")
    new_manager = EndpointManager(
        config_path="config/endpoints.json",
        auto_load=True
    )

    print(f"   ✅ Loaded {len(new_manager.endpoints)} endpoints")

    # Verify loaded data
    for name, endpoint in new_manager.endpoints.items():
        print(f"      - {name}: {endpoint.url}")


def example_skill_integration():
    """Example of how a skill would integrate with the endpoint manager."""
    print("\n" + "=" * 60)
    print("Example 8: Skill Integration Pattern")
    print("=" * 60)

    print("\n📝 Example skill code:\n")
    print("""
class EmbeddingSkill:
    def __init__(self, endpoint_manager):
        self.endpoint_manager = endpoint_manager

    def generate_embedding(self, text):
        # Query the endpoint manager for the embedding API
        request = EndpointQueryRequest(
            endpoint_name="openai_embeddings",
            include_credentials=True,
            validate_health=True  # Ensure it's healthy
        )

        response = self.endpoint_manager.query_endpoint(request)

        if not response.available:
            raise RuntimeError("Embedding API not available")

        endpoint = response.endpoint

        # Check rate limit
        if not self.endpoint_manager.check_rate_limit(endpoint.name):
            self.endpoint_manager.wait_for_rate_limit(endpoint.name)

        # Make the actual API call
        import requests
        headers = endpoint.get_headers()
        headers['Content-Type'] = 'application/json'

        response = requests.post(
            endpoint.url,
            headers=headers,
            json={"input": text, "model": "text-embedding-ada-002"},
            timeout=endpoint.timeout
        )

        # Record the request for rate limiting
        self.endpoint_manager.record_request(endpoint.name)

        return response.json()
    """)

    print("\n💡 Key benefits:")
    print("   ✓ Centralized credential management")
    print("   ✓ Automatic health checking")
    print("   ✓ Built-in rate limiting")
    print("   ✓ Easy endpoint switching/rotation")
    print("   ✓ Configuration-driven (no code changes needed)")


def main():
    """Run all examples."""
    print("\n🚀 API Endpoint Manager Examples\n")

    # Basic usage
    manager = example_basic_usage()

    # Health checking
    example_health_checking(manager)

    # Querying (skill usage)
    example_querying_endpoints(manager)

    # API key rotation
    example_api_key_rotation(manager)

    # Rate limiting
    example_rate_limiting(manager)

    # Filtering and statistics
    example_filtering_and_statistics(manager)

    # Persistence
    example_persistence(manager)

    # Skill integration pattern
    example_skill_integration()

    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("=" * 60)
    print(f"\nConfiguration saved to: {manager.config_path}")
    print("You can now load this configuration in your applications.\n")


if __name__ == "__main__":
    main()
