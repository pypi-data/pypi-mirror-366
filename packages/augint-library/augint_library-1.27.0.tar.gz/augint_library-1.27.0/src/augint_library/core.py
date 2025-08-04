"""Core library functions for augint-library.

This module contains the main library functions that can be imported and used
in other Python code. These functions are wrapped by the CLI but can also
be used directly as a library.
"""

import random
import time
from typing import Any

from .exceptions import NetworkError, NetworkTimeoutError


def print_hi(name: str) -> None:
    """Print a friendly greeting to the given name.

    This is the main library function that can be imported and used
    in other Python code. Updated for Dependabot testing workflow.

    Args:
        name: The name of the person to greet.

    Example:
        >>> print_hi("Alice")
        Hi Alice
    """
    print(f"Hi {name}")


def fetch_data(endpoint: str, timeout: float = 1.0, failure_rate: float = 0.3) -> dict[str, Any]:
    """Fetch data from a remote endpoint (simulated).

    This function simulates an external API call that might fail transiently.
    It's designed to demonstrate when retry and circuit breaker patterns are useful.

    In a real application, this would make an actual HTTP request to an external service.
    The simulation allows us to control failure rates for testing and demonstration.

    Args:
        endpoint: The API endpoint to fetch from.
        timeout: Maximum time to wait for response (seconds).
        failure_rate: Probability of failure (0.0-1.0) for simulation.

    Returns:
        A dictionary containing the fetched data.

    Raises:
        NetworkTimeoutError: If the request times out.
        NetworkError: If the network request fails.

    Example:
        >>> # This might fail transiently
        >>> data = fetch_data("/api/users")
        >>> print(data["status"])
        ok
    """
    # Simulate network delay
    if failure_rate > 0:
        # Allow delays that might exceed timeout when failures are possible
        delay = random.uniform(0.1, timeout * 1.2)  # noqa: S311 - simulation only
    else:
        # When failure_rate is 0, ensure we never timeout
        delay = random.uniform(0.1, timeout * 0.8)  # noqa: S311 - simulation only

    if delay > timeout:
        raise NetworkTimeoutError(
            service=f"API endpoint {endpoint}", timeout=timeout, attempted_duration=delay
        )

    time.sleep(delay)

    # Simulate random failures (but not when failure_rate is 0)
    if failure_rate > 0 and random.random() < failure_rate:  # noqa: S311 - simulation only
        raise NetworkError(
            f"Failed to connect to {endpoint}", service=f"API endpoint {endpoint}", status_code=503
        )

    # Return simulated successful response
    return {
        "status": "ok",
        "endpoint": endpoint,
        "data": {"users": ["Alice", "Bob", "Charlie"]},
        "timestamp": time.time(),
    }
