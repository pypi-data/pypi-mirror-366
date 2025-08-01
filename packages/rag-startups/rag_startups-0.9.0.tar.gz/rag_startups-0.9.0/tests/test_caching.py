"""Tests for caching functionality."""

import os
import time

from rag_startups.utils.caching import cache_result, get_redis_client


def test_fakeredis_basic():
    """Test basic fakeredis functionality."""
    # Clear any existing Redis settings
    os.environ.pop("REDIS_HOST", None)
    os.environ.pop("REDIS_PORT", None)

    # Should get fakeredis client
    redis_client = get_redis_client()
    assert redis_client is not None

    # Test basic operations
    call_count = 0

    @cache_result(ttl_seconds=60)
    def sample_function(x):
        nonlocal call_count
        call_count += 1
        return x * 2

    # Should cache the result
    result1 = sample_function(5)
    assert result1 == 10

    # Should return cached result
    result2 = sample_function(5)
    assert result2 == 10
    assert call_count == 1  # Should not have called function again


def test_ttl_cache_fallback():
    """Test fallback to TTLCache when Redis is unavailable."""
    # Force Redis to be unavailable
    os.environ["REDIS_HOST"] = "nonexistent_host"

    call_count = 0

    @cache_result(ttl_seconds=1)
    def sample_function(x):
        nonlocal call_count
        call_count += 1
        return x * 2

    # Should use TTLCache
    result1 = sample_function(5)
    assert result1 == 10
    assert call_count == 1

    # Should return cached result
    result2 = sample_function(5)
    assert result2 == 10
    assert call_count == 1  # Should not have called function again

    # Wait for TTL to expire
    time.sleep(1.1)

    # Should recompute after TTL expires
    result3 = sample_function(5)
    assert result3 == 10  # Value should be same
    assert call_count == 2  # Should have called function again


def test_cache_error_handling():
    """Test that functions still work when caching fails."""
    # Clear any existing Redis settings
    os.environ.pop("REDIS_HOST", None)
    os.environ.pop("REDIS_PORT", None)

    call_count = 0

    @cache_result(ttl_seconds=60)
    def sample_function(x):
        nonlocal call_count
        call_count += 1
        return x * 2

    # First call should work and cache
    result1 = sample_function(5)
    assert result1 == 10
    assert call_count == 1

    # Second call should use cache
    result2 = sample_function(5)
    assert result2 == 10
    assert call_count == 1  # Shouldn't have called function again

    # Force cache error by setting invalid host
    os.environ["REDIS_HOST"] = "nonexistent_host"

    # Should still work, but will call function again
    result3 = sample_function(5)
    assert result3 == 10
    assert call_count == 2  # Should have called function again


def test_concurrent_access():
    """Test cache behavior with concurrent access."""
    from concurrent.futures import ThreadPoolExecutor

    # Clear any existing Redis settings
    os.environ.pop("REDIS_HOST", None)
    os.environ.pop("REDIS_PORT", None)

    call_count = 0

    @cache_result(ttl_seconds=60)
    def sample_function(x):
        nonlocal call_count
        call_count += 1
        time.sleep(0.1)  # Simulate some work
        return x * 2

    # Run multiple concurrent calls
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(sample_function, 5) for _ in range(10)]
        results = [f.result() for f in futures]

    # All results should be correct
    assert all(r == 10 for r in results)

    # Should have only called function once due to caching
    assert call_count == 1
