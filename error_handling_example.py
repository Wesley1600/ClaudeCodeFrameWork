"""
Error Handling Example - Robust Retry Logic with Fallbacks

This module demonstrates the error handling patterns from the Claude Code
error-handling skill, implemented in Python for common operations.

Use this as a reference for implementing similar error handling in your applications.
"""

import time
import functools
import logging
from typing import Callable, Any, Optional, TypeVar, Type
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

T = TypeVar('T')


class ErrorType(Enum):
    """Classification of error types for handling strategy"""
    RETRYABLE = "retryable"
    NON_RETRYABLE = "non-retryable"
    CRITICAL = "critical"


class RetryConfig:
    """Configuration for retry behavior"""
    def __init__(
        self,
        max_retries: int = 4,
        base_delay: float = 2.0,
        max_delay: float = 16.0,
        exponential_base: float = 2.0
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number"""
        delay = self.base_delay * (self.exponential_base ** attempt)
        return min(delay, self.max_delay)


class OperationError(Exception):
    """Base exception for operation errors with classification"""
    def __init__(self, message: str, error_type: ErrorType, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.error_type = error_type
        self.original_error = original_error


def classify_error(error: Exception) -> ErrorType:
    """
    Classify an error to determine handling strategy

    Args:
        error: The exception to classify

    Returns:
        ErrorType indicating how to handle the error
    """
    error_str = str(error).lower()

    # Retryable errors (network, temporary issues)
    retryable_patterns = [
        'timeout', 'timed out', 'connection', 'network',
        'temporary', 'busy', 'locked', '429', '503', '504',
        'rate limit', 'try again'
    ]

    # Critical errors (data corruption, security)
    critical_patterns = [
        'corruption', 'corrupt', 'security', 'vulnerability',
        'malfunction', 'unexpected state'
    ]

    # Check for critical errors first
    if any(pattern in error_str for pattern in critical_patterns):
        return ErrorType.CRITICAL

    # Check for retryable errors
    if any(pattern in error_str for pattern in retryable_patterns):
        return ErrorType.RETRYABLE

    # Default to non-retryable
    return ErrorType.NON_RETRYABLE


def with_retry(
    config: Optional[RetryConfig] = None,
    fallback: Optional[Callable] = None,
    error_classifier: Callable[[Exception], ErrorType] = classify_error
):
    """
    Decorator that adds retry logic with exponential backoff and fallback

    Args:
        config: RetryConfig with retry parameters
        fallback: Optional fallback function to call if all retries fail
        error_classifier: Function to classify errors

    Example:
        @with_retry(config=RetryConfig(max_retries=3))
        def fetch_data(url):
            return requests.get(url)
    """
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_error = None

            for attempt in range(config.max_retries + 1):
                try:
                    # Log attempt
                    if attempt > 0:
                        logger.info(
                            f"Retry attempt {attempt}/{config.max_retries} "
                            f"for {func.__name__}"
                        )

                    # Execute function
                    result = func(*args, **kwargs)

                    # Log success after retry
                    if attempt > 0:
                        logger.info(
                            f"{func.__name__} succeeded after {attempt} retries"
                        )

                    return result

                except Exception as e:
                    last_error = e
                    error_type = error_classifier(e)

                    # Log error
                    logger.error(
                        f"[ERROR] {func.__name__}\n"
                        f"  Attempt: {attempt + 1}/{config.max_retries + 1}\n"
                        f"  Error Type: {error_type.value}\n"
                        f"  Error: {str(e)}"
                    )

                    # Handle critical errors immediately
                    if error_type == ErrorType.CRITICAL:
                        logger.critical(
                            f"Critical error in {func.__name__}: {str(e)}\n"
                            f"Escalating for human review"
                        )
                        raise OperationError(
                            f"Critical error: {str(e)}",
                            ErrorType.CRITICAL,
                            e
                        )

                    # Don't retry non-retryable errors
                    if error_type == ErrorType.NON_RETRYABLE:
                        logger.warning(
                            f"Non-retryable error in {func.__name__}, "
                            f"attempting fallback"
                        )
                        break

                    # Check if we should retry
                    if attempt < config.max_retries:
                        delay = config.get_delay(attempt)
                        logger.info(f"Waiting {delay}s before retry...")
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"Max retries ({config.max_retries}) exceeded "
                            f"for {func.__name__}"
                        )

            # All retries exhausted, try fallback
            if fallback is not None:
                logger.info(
                    f"Attempting fallback for {func.__name__}"
                )
                try:
                    result = fallback(*args, **kwargs)
                    logger.info(
                        f"Fallback succeeded for {func.__name__}"
                    )
                    return result
                except Exception as fallback_error:
                    logger.error(
                        f"Fallback failed for {func.__name__}: "
                        f"{str(fallback_error)}"
                    )
                    raise OperationError(
                        f"Both primary and fallback failed. "
                        f"Primary: {str(last_error)}, "
                        f"Fallback: {str(fallback_error)}",
                        ErrorType.NON_RETRYABLE,
                        last_error
                    )

            # No fallback or fallback not applicable
            raise OperationError(
                f"Operation failed after {config.max_retries} retries: "
                f"{str(last_error)}",
                ErrorType.NON_RETRYABLE,
                last_error
            )

        return wrapper
    return decorator


# Example usage scenarios

def example_network_operation_with_retry():
    """Example: Network operation with automatic retry"""

    @with_retry(config=RetryConfig(max_retries=3, base_delay=2.0))
    def fetch_url(url: str) -> str:
        """Simulated network fetch that might fail"""
        import random
        if random.random() < 0.7:  # 70% chance of failure
            raise ConnectionError("Network timeout")
        return f"Content from {url}"

    try:
        result = fetch_url("https://example.com")
        print(f"Success: {result}")
    except OperationError as e:
        print(f"Failed after retries: {e}")


def example_with_fallback():
    """Example: Operation with fallback strategy"""

    def primary_operation(file_path: str) -> str:
        """Primary operation that might fail"""
        # Simulated file read that fails
        raise PermissionError(f"Cannot read {file_path}")

    def fallback_operation(file_path: str) -> str:
        """Fallback: try alternative approach"""
        logger.info(f"Using fallback: reading with lower permissions")
        return f"Fallback content from {file_path}"

    @with_retry(
        config=RetryConfig(max_retries=2),
        fallback=fallback_operation
    )
    def read_file(file_path: str) -> str:
        return primary_operation(file_path)

    try:
        result = read_file("/path/to/file.txt")
        print(f"Success: {result}")
    except OperationError as e:
        print(f"Operation failed: {e}")


def example_git_push_with_retry():
    """Example: Git push with network retry logic"""
    import subprocess

    def git_push_fallback(branch: str) -> str:
        """Fallback: try with different remote or strategy"""
        logger.info("Attempting git push with --force-with-lease")
        # In real implementation, this would execute alternative strategy
        return f"Pushed {branch} using fallback strategy"

    @with_retry(
        config=RetryConfig(max_retries=4, base_delay=2.0),
        fallback=git_push_fallback
    )
    def git_push(branch: str) -> str:
        """Push to git with retry on network failures"""
        try:
            result = subprocess.run(
                ['git', 'push', '-u', 'origin', branch],
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            raise TimeoutError("Git push timed out")
        except subprocess.CalledProcessError as e:
            # Classify git errors
            if 'connection' in e.stderr.lower() or 'timeout' in e.stderr.lower():
                raise ConnectionError(f"Network error: {e.stderr}")
            else:
                raise RuntimeError(f"Git push failed: {e.stderr}")

    try:
        result = git_push("feature-branch")
        print(f"Git push successful: {result}")
    except OperationError as e:
        print(f"Git push failed: {e}")
        print("Please check your network connection and try again")


def example_multi_step_with_recovery():
    """Example: Multi-step operation with recovery at each step"""

    class DatabaseOperation:
        def __init__(self):
            self.transaction_log = []

        @with_retry(config=RetryConfig(max_retries=3))
        def connect(self):
            """Connect to database with retry"""
            logger.info("Connecting to database...")
            # Simulated connection
            self.transaction_log.append("connected")
            return True

        @with_retry(config=RetryConfig(max_retries=2))
        def execute_query(self, query: str):
            """Execute query with retry"""
            logger.info(f"Executing: {query}")
            self.transaction_log.append(f"executed: {query}")
            return f"Result of {query}"

        def rollback(self):
            """Rollback on failure"""
            logger.warning("Rolling back transaction...")
            self.transaction_log.append("rolled_back")

        def commit(self):
            """Commit transaction"""
            logger.info("Committing transaction...")
            self.transaction_log.append("committed")

    db = DatabaseOperation()
    try:
        db.connect()
        db.execute_query("INSERT INTO users ...")
        db.execute_query("UPDATE stats ...")
        db.commit()
        print("Transaction completed successfully")
    except OperationError as e:
        logger.error(f"Transaction failed: {e}")
        db.rollback()
        print("Transaction rolled back due to error")


if __name__ == "__main__":
    print("=== Error Handling Examples ===\n")

    print("1. Network operation with retry:")
    example_network_operation_with_retry()
    print()

    print("2. Operation with fallback:")
    example_with_fallback()
    print()

    print("3. Multi-step operation with recovery:")
    example_multi_step_with_recovery()
    print()

    print("\n=== Examples completed ===")
