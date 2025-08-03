from abc import ABC, abstractmethod
from collections.abc import Awaitable
from typing import Any, Optional, Union

from pyjupiter.exceptions import JupiterValidationError
from pyjupiter.models.ultra_api.ultra_execute_request_model import (
    UltraExecuteRequest,
)
from pyjupiter.models.ultra_api.ultra_order_request_model import (
    UltraOrderRequest,
)


class BaseUltraClient(ABC):
    """
    Abstract base class for Ultra API clients providing common HTTP methods.

    This class defines the interface and common logic for both synchronous
    and asynchronous Ultra API client implementations.
    """

    @abstractmethod
    def _make_get_request(
        self, url: str, params: Optional[dict[str, Any]] = None, headers: Optional[dict[str, str]] = None
    ) -> Union[dict[str, Any], Awaitable[dict[str, Any]]]:
        """
        Make a GET request. Implementation depends on sync/async nature.

        Args:
            url: The URL to make the request to.
            params: Optional query parameters.
            headers: Optional request headers.

        Returns:
            Response JSON data (sync) or awaitable response (async).
        """
        pass

    @abstractmethod
    def _make_post_request(
        self, url: str, json: Optional[dict[str, Any]] = None, headers: Optional[dict[str, str]] = None
    ) -> Union[dict[str, Any], Awaitable[dict[str, Any]]]:
        """
        Make a POST request. Implementation depends on sync/async nature.

        Args:
            url: The URL to make the request to.
            json: Optional JSON payload.
            headers: Optional request headers.

        Returns:
            Response JSON data (sync) or awaitable response (async).
        """
        pass

    @abstractmethod
    def _call_order(self, request: UltraOrderRequest) -> Union[dict[str, Any], Awaitable[dict[str, Any]]]:
        """
        Call the order method. Implementation depends on sync/async nature.

        Args:
            request: The order request parameters.

        Returns:
            Order response (sync) or awaitable response (async).
        """
        pass

    @abstractmethod
    def _call_execute(self, request: UltraExecuteRequest) -> Union[dict[str, Any], Awaitable[dict[str, Any]]]:
        """
        Call the execute method. Implementation depends on sync/async nature.

        Args:
            request: The execute request parameters.

        Returns:
            Execute response (sync) or awaitable response (async).
        """
        pass

    def _build_order_url(self) -> str:
        """Build the order endpoint URL."""
        return f"{self.base_url}/ultra/v1/order"  # type: ignore[attr-defined]

    def _build_execute_url(self) -> str:
        """Build the execute endpoint URL."""
        return f"{self.base_url}/ultra/v1/execute"  # type: ignore[attr-defined]

    def _build_balances_url(self, address: str) -> str:
        """Build the balances endpoint URL."""
        return f"{self.base_url}/ultra/v1/balances/{address}"  # type: ignore[attr-defined]

    def _build_shield_url(self) -> str:
        """Build the shield endpoint URL."""
        return f"{self.base_url}/ultra/v1/shield"  # type: ignore[attr-defined]

    def _prepare_order_params(self, request: UltraOrderRequest) -> dict[str, Any]:
        """Prepare parameters for order request."""
        return request.to_dict()

    def _prepare_execute_payload(self, request: UltraExecuteRequest) -> dict[str, Any]:
        """Prepare payload for execute request."""
        return request.to_dict()

    def _prepare_shield_params(self, mints: list[str]) -> dict[str, str]:
        """Prepare parameters for shield request."""
        return {"mints": ",".join(mints)}

    def _prepare_execute_request_from_order(self, order_response: dict[str, Any]) -> UltraExecuteRequest:
        """
        Prepare execute request from order response.

        Args:
            order_response: Response from the order endpoint.

        Returns:
            UltraExecuteRequest prepared for execution.

        Raises:
            JupiterValidationError: If order response is missing required fields.
        """
        # Validate order response structure
        if not isinstance(order_response, dict):
            raise JupiterValidationError(
                "Invalid order response: expected dictionary", value=type(order_response).__name__
            )

        if "requestId" not in order_response:
            raise JupiterValidationError("Order response missing required field: requestId", field="requestId")

        if "transaction" not in order_response:
            raise JupiterValidationError("Order response missing required field: transaction", field="transaction")

        transaction_data = order_response["transaction"]
        if not transaction_data or not isinstance(transaction_data, str):
            raise JupiterValidationError(
                "Order response contains invalid transaction data", field="transaction", value=transaction_data
            )

        request_id = order_response["requestId"]
        signed_transaction = self._sign_base64_transaction(transaction_data)  # type: ignore[attr-defined]

        return UltraExecuteRequest(
            request_id=request_id,
            signed_transaction=self._serialize_versioned_transaction(signed_transaction),  # type: ignore[attr-defined]
        )
