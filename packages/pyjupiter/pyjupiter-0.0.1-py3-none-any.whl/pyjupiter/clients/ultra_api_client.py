import contextlib
from typing import Any, Optional

from curl_cffi.requests import RequestsError

from pyjupiter.clients.base_ultra_client import BaseUltraClient
from pyjupiter.clients.jupiter_client import AsyncJupiterClient, JupiterClient
from pyjupiter.exceptions import (
    JupiterAPIError,
    JupiterAuthenticationError,
    JupiterNetworkError,
    JupiterRateLimitError,
    JupiterValidationError,
)
from pyjupiter.models.ultra_api.ultra_execute_request_model import (
    UltraExecuteRequest,
)
from pyjupiter.models.ultra_api.ultra_order_request_model import (
    UltraOrderRequest,
)


class UltraApiClient(JupiterClient, BaseUltraClient):
    """
    A synchronous client for interacting with the Jupiter Ultra API.
    """

    def _handle_response(self, response) -> dict[str, Any]:
        """
        Handle HTTP response and convert errors to custom exceptions.

        Args:
            response: The HTTP response object from curl_cffi.

        Returns:
            dict: The parsed JSON response data.

        Raises:
            JupiterAuthenticationError: For 401/403 status codes.
            JupiterRateLimitError: For 429 status code.
            JupiterAPIError: For other HTTP error status codes.
            JupiterNetworkError: For network-related errors.
            JupiterValidationError: For invalid response data.
        """
        try:
            response.raise_for_status()
            response_data = response.json()

            # Validate response structure
            if not isinstance(response_data, dict):
                raise JupiterValidationError(
                    "Invalid response format: expected JSON object", value=type(response_data).__name__
                )

            # Check for API error messages
            if "errorMessage" in response_data:
                raise JupiterAPIError(
                    f"API Error: {response_data['errorMessage']}",
                    status_code=response.status_code,
                    response_data=response_data,
                )

            return response_data  # type: ignore[no-any-return]

        except RequestsError as e:
            status_code = e.response.status_code if hasattr(e, "response") and e.response else None

            # Try to get response data for error details
            response_data = {}
            try:
                if hasattr(e, "response") and e.response:
                    response_data = e.response.json()
            except Exception:
                # If we can't parse the response, just use the status code
                pass

            if status_code == 401:
                raise JupiterAuthenticationError(
                    "Authentication failed: Invalid API key or unauthorized access",
                    status_code=status_code,
                    response_data=response_data,
                ) from e
            elif status_code == 403:
                raise JupiterAuthenticationError(
                    "Access forbidden: Insufficient permissions", status_code=status_code, response_data=response_data
                ) from e
            elif status_code == 429:
                # Extract retry-after header if available
                retry_after = None
                if hasattr(e, "response") and e.response and hasattr(e.response, "headers"):
                    retry_after_header = e.response.headers.get("retry-after")
                    if retry_after_header:
                        with contextlib.suppress(ValueError):
                            retry_after = int(retry_after_header)

                raise JupiterRateLimitError(
                    "Rate limit exceeded. Please try again later.",
                    retry_after=retry_after,
                    status_code=status_code,
                    response_data=response_data,
                ) from e
            else:
                error_message = f"HTTP {status_code} error"
                if response_data and "errorMessage" in response_data:
                    error_message = response_data["errorMessage"]
                elif response_data and "message" in response_data:
                    error_message = response_data["message"]

                raise JupiterAPIError(error_message, status_code=status_code, response_data=response_data) from e

        except Exception as e:
            # Handle network errors and other exceptions
            if isinstance(
                e, (JupiterAPIError, JupiterAuthenticationError, JupiterRateLimitError, JupiterValidationError)
            ):
                # Re-raise our custom exceptions
                raise

            # Convert other exceptions to network errors
            raise JupiterNetworkError(f"Network error occurred: {e!s}", original_error=e) from e

    def _make_get_request(
        self, url: str, params: Optional[dict[str, Any]] = None, headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        """Make a synchronous GET request."""
        response = self.client.get(url, params=params, headers=headers)
        return self._handle_response(response)

    def _make_post_request(
        self, url: str, json: Optional[dict[str, Any]] = None, headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        """Make a synchronous POST request."""
        response = self.client.post(url, json=json, headers=headers)
        return self._handle_response(response)

    def _call_order(self, request: UltraOrderRequest) -> dict[str, Any]:
        """Call the synchronous order method."""
        return self.order(request)

    def _call_execute(self, request: UltraExecuteRequest) -> dict[str, Any]:
        """Call the synchronous execute method."""
        return self.execute(request)

    def order(self, request: UltraOrderRequest) -> dict[str, Any]:
        """
        Get an order from the Jupiter Ultra API (synchronous).

        Args:
            request (UltraOrderRequest): The request parameters for the order.

        Returns:
            dict: The dict api response.
        """
        params = self._prepare_order_params(request)
        url = self._build_order_url()
        return self._make_get_request(url, params=params, headers=self._get_headers())

    def execute(self, request: UltraExecuteRequest) -> dict[str, Any]:
        """
        Execute the order with the Jupiter Ultra API (synchronous).

        Args:
            request (UltraExecuteRequest): The execute request parameters.

        Returns:
            dict: The dict api response.
        """
        payload = self._prepare_execute_payload(request)
        url = self._build_execute_url()
        return self._make_post_request(url, json=payload, headers=self._get_headers())

    def order_and_execute(self, request: UltraOrderRequest) -> dict[str, Any]:
        """
        Get and execute an order in a single call (synchronous).

        Args:
            request (UltraOrderRequest): The request parameters for the order.

        Returns:
            dict: The dict api response.
        """
        order_response = self._call_order(request)
        execute_request = self._prepare_execute_request_from_order(order_response)
        return self._call_execute(execute_request)

    def balances(self, address: str) -> dict[str, Any]:
        """
        Get token balances of an account (synchronous).

        Args:
            address (str): The public key of the account to get balances for.

        Returns:
            dict: The dict api response.
        """
        url = self._build_balances_url(address)
        return self._make_get_request(url, headers=self._get_headers())

    def shield(self, mints: list[str]) -> dict[str, Any]:
        """
        Get token info and warnings for specific mints (synchronous).

        Args:
            mints (list[str]): List of token mint addresses
            to get information for.

        Returns:
            dict: The dict api response with warnings information.
        """
        params = self._prepare_shield_params(mints)
        url = self._build_shield_url()
        return self._make_get_request(url, params=params, headers=self._get_headers())


class AsyncUltraApiClient(AsyncJupiterClient, BaseUltraClient):
    """
    An asynchronous client for interacting with the Jupiter Ultra API.
    """

    async def _handle_response(self, response) -> dict[str, Any]:
        """
        Handle HTTP response and convert errors to custom exceptions (async version).

        Args:
            response: The HTTP response object from curl_cffi.

        Returns:
            dict: The parsed JSON response data.

        Raises:
            JupiterAuthenticationError: For 401/403 status codes.
            JupiterRateLimitError: For 429 status code.
            JupiterAPIError: For other HTTP error status codes.
            JupiterNetworkError: For network-related errors.
            JupiterValidationError: For invalid response data.
        """
        try:
            response.raise_for_status()
            response_data = response.json()

            # Validate response structure
            if not isinstance(response_data, dict):
                raise JupiterValidationError(
                    "Invalid response format: expected JSON object", value=type(response_data).__name__
                )

            # Check for API error messages
            if "errorMessage" in response_data:
                raise JupiterAPIError(
                    f"API Error: {response_data['errorMessage']}",
                    status_code=response.status_code,
                    response_data=response_data,
                )

            return response_data  # type: ignore[no-any-return]

        except RequestsError as e:
            status_code = e.response.status_code if hasattr(e, "response") and e.response else None

            # Try to get response data for error details
            response_data = {}
            try:
                if hasattr(e, "response") and e.response:
                    response_data = e.response.json()
            except Exception:
                # If we can't parse the response, just use the status code
                pass

            if status_code == 401:
                raise JupiterAuthenticationError(
                    "Authentication failed: Invalid API key or unauthorized access",
                    status_code=status_code,
                    response_data=response_data,
                ) from e
            elif status_code == 403:
                raise JupiterAuthenticationError(
                    "Access forbidden: Insufficient permissions", status_code=status_code, response_data=response_data
                ) from e
            elif status_code == 429:
                # Extract retry-after header if available
                retry_after = None
                if hasattr(e, "response") and e.response and hasattr(e.response, "headers"):
                    retry_after_header = e.response.headers.get("retry-after")
                    if retry_after_header:
                        with contextlib.suppress(ValueError):
                            retry_after = int(retry_after_header)

                raise JupiterRateLimitError(
                    "Rate limit exceeded. Please try again later.",
                    retry_after=retry_after,
                    status_code=status_code,
                    response_data=response_data,
                ) from e
            else:
                error_message = f"HTTP {status_code} error"
                if response_data and "errorMessage" in response_data:
                    error_message = response_data["errorMessage"]
                elif response_data and "message" in response_data:
                    error_message = response_data["message"]

                raise JupiterAPIError(error_message, status_code=status_code, response_data=response_data) from e

        except Exception as e:
            # Handle network errors and other exceptions
            if isinstance(
                e, (JupiterAPIError, JupiterAuthenticationError, JupiterRateLimitError, JupiterValidationError)
            ):
                # Re-raise our custom exceptions
                raise

            # Convert other exceptions to network errors
            raise JupiterNetworkError(f"Network error occurred: {e!s}", original_error=e) from e

    async def _make_get_request(
        self, url: str, params: Optional[dict[str, Any]] = None, headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        """Make an asynchronous GET request."""
        response = await self.client.get(url, params=params, headers=headers)
        return await self._handle_response(response)

    async def _make_post_request(
        self, url: str, json: Optional[dict[str, Any]] = None, headers: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        """Make an asynchronous POST request."""
        response = await self.client.post(url, json=json, headers=headers)
        return await self._handle_response(response)

    async def _call_order(self, request: UltraOrderRequest) -> dict[str, Any]:
        """Call the asynchronous order method."""
        return await self.order(request)

    async def _call_execute(self, request: UltraExecuteRequest) -> dict[str, Any]:
        """Call the asynchronous execute method."""
        return await self.execute(request)

    async def order(self, request: UltraOrderRequest) -> dict[str, Any]:
        """
        Get an order from the Jupiter Ultra API (asynchronous).

        Args:
            request (UltraOrderRequest): The request parameters for the order.

        Returns:
            dict: The dict api response.
        """
        params = self._prepare_order_params(request)
        url = self._build_order_url()
        return await self._make_get_request(url, params=params, headers=self._get_headers())

    async def execute(self, request: UltraExecuteRequest) -> dict[str, Any]:
        """
        Execute the order with the Jupiter Ultra API (asynchronous).

        Args:
            request (UltraExecuteRequest): The execute request parameters.

        Returns:
            dict: The dict api response.
        """
        payload = self._prepare_execute_payload(request)
        url = self._build_execute_url()
        return await self._make_post_request(url, json=payload, headers=self._get_headers())

    async def order_and_execute(self, request: UltraOrderRequest) -> dict[str, Any]:
        """
        Get and execute an order in a single call (asynchronous).

        Args:
            request (UltraOrderRequest): The request parameters for the order.

        Returns:
            dict: The dict api response.
        """
        order_response = await self._call_order(request)
        execute_request = self._prepare_execute_request_from_order(order_response)
        return await self._call_execute(execute_request)

    async def balances(self, address: str) -> dict[str, Any]:
        """
        Get token balances of an account (asynchronous).

        Args:
            address (str): The public key of the account to get balances for.

        Returns:
            dict: The dict api response.
        """
        url = self._build_balances_url(address)
        return await self._make_get_request(url, headers=self._get_headers())

    async def shield(self, mints: list[str]) -> dict[str, Any]:
        """
        Get token info and warnings for specific mints (asynchronous).

        Args:
            mints (list[str]): List of token mint addresses
            to get information for.

        Returns:
            dict: The dict api response with warnings information.
        """
        params = self._prepare_shield_params(mints)
        url = self._build_shield_url()
        return await self._make_get_request(url, params=params, headers=self._get_headers())
