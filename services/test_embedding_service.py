"""
Quick tests for the embedding service.

Run these after starting the service to verify it's working correctly.
"""

import asyncio
import httpx
import pytest


BASE_URL = "http://localhost:8000"


async def test_health():
    """Test health endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "starting"]
        assert "device" in data
        print(f"✓ Health check passed - Status: {data['status']}, Device: {data['device']}")


async def test_ready():
    """Test readiness endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/ready")
        if response.status_code == 200:
            print("✓ Service is ready")
        else:
            print("⚠ Service not ready yet (may still be loading model)")


async def test_single_embedding():
    """Test single text embedding"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{BASE_URL}/v1/embeddings",
            json={
                "model": "Qwen/Qwen3-Embedding-4B",
                "input": "This is a test document for embedding",
                "dimensions": 1024,
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["object"] == "list"
        assert len(data["data"]) == 1
        assert len(data["data"][0]["embedding"]) == 1024
        print(f"✓ Single embedding test passed - Got {len(data['data'][0]['embedding'])} dimensions")


async def test_batch_embedding():
    """Test batch embedding"""
    texts = [
        "First document about machine learning",
        "Second document about databases",
        "Third document about APIs",
    ]

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{BASE_URL}/v1/embeddings",
            json={
                "model": "Qwen/Qwen3-Embedding-4B",
                "input": texts,
                "dimensions": 512,
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 3
        assert all(len(item["embedding"]) == 512 for item in data["data"])
        print(f"✓ Batch embedding test passed - Processed {len(texts)} texts")


async def test_full_dimensions():
    """Test full dimension embedding"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{BASE_URL}/v1/embeddings",
            json={
                "model": "Qwen/Qwen3-Embedding-4B",
                "input": "Full dimension test",
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Should default to BASE_DIM (2560)
        assert len(data["data"][0]["embedding"]) == 2560
        print(f"✓ Full dimension test passed - Got {len(data['data'][0]['embedding'])} dimensions")


async def test_base64_encoding():
    """Test base64 encoding format"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{BASE_URL}/v1/embeddings",
            json={
                "model": "Qwen/Qwen3-Embedding-4B",
                "input": "Test base64 encoding",
                "dimensions": 256,
                "encoding_format": "base64",
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Should be base64 string
        assert isinstance(data["data"][0]["embedding"], str)
        print("✓ Base64 encoding test passed")


async def test_error_empty_input():
    """Test error handling for empty input"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/v1/embeddings",
            json={
                "model": "Qwen/Qwen3-Embedding-4B",
                "input": "",
            }
        )
        assert response.status_code == 422  # Validation error
        print("✓ Empty input validation test passed")


async def test_error_invalid_dimensions():
    """Test error handling for invalid dimensions"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/v1/embeddings",
            json={
                "model": "Qwen/Qwen3-Embedding-4B",
                "input": "test",
                "dimensions": 10,  # Too small
            }
        )
        assert response.status_code == 422  # Validation error
        print("✓ Invalid dimension validation test passed")


async def test_models_endpoint():
    """Test models listing endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/v1/models")
        assert response.status_code == 200
        data = response.json()
        assert data["object"] == "list"
        assert len(data["data"]) > 0
        print(f"✓ Models endpoint test passed - Found {len(data['data'])} model(s)")


async def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Testing Qwen3 Embedding Service")
    print("=" * 60)

    tests = [
        ("Health Check", test_health),
        ("Readiness Check", test_ready),
        ("Models Endpoint", test_models_endpoint),
        ("Single Embedding", test_single_embedding),
        ("Batch Embedding", test_batch_embedding),
        ("Full Dimensions", test_full_dimensions),
        ("Base64 Encoding", test_base64_encoding),
        ("Empty Input Error", test_error_empty_input),
        ("Invalid Dimensions Error", test_error_invalid_dimensions),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        print(f"\n[{name}]")
        try:
            await test_func()
            passed += 1
        except httpx.ConnectError:
            print(f"✗ Connection failed - Is the service running on {BASE_URL}?")
            print("  Start the service with: python embedding_service.py")
            break
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
