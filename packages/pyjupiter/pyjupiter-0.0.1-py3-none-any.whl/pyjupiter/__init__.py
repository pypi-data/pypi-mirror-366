"""
Jupiter Python SDK - A comprehensive Python SDK for interacting with Jupiter APIs.

This package provides both synchronous and asynchronous clients for interacting
with Jupiter's swap and trading APIs, including the Ultra API for advanced trading features.
"""

# Import client classes
from pyjupiter.clients.jupiter_client import AsyncJupiterClient, JupiterClient
from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient, UltraApiClient

# Import exception classes
from pyjupiter.exceptions import (
    JupiterAPIError,
    JupiterAuthenticationError,
    JupiterError,
    JupiterNetworkError,
    JupiterRateLimitError,
    JupiterValidationError,
)

# Import model classes
from pyjupiter.models.ultra_api.ultra_execute_request_model import UltraExecuteRequest
from pyjupiter.models.ultra_api.ultra_order_request_model import UltraOrderRequest

__version__ = "0.1.0"

__all__ = [
    # Client classes
    "AsyncJupiterClient",
    "AsyncUltraApiClient",
    # Exception classes
    "JupiterAPIError",
    "JupiterAuthenticationError",
    "JupiterClient",
    "JupiterError",
    "JupiterNetworkError",
    "JupiterRateLimitError",
    "JupiterValidationError",
    "UltraApiClient",
    # Model classes
    "UltraExecuteRequest",
    "UltraOrderRequest",
]
