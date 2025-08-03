import base64
import json
import os
from typing import Any, Optional

import base58
from curl_cffi import AsyncSession, requests
from solders.solders import Keypair, VersionedTransaction

from pyjupiter.exceptions import JupiterValidationError


class _CoreJupiterClient:
    """
    Core non-network-dependent logic for Jupiter clients.
    Handles private key loading and transaction signing.
    """

    def __init__(self, api_key: Optional[str], private_key_env_var: str):
        """
        Initialize the core Jupiter client.

        Args:
            api_key: Optional API key for enhanced access to Jupiter API.
                If provided, uses https://api.jup.ag endpoint.
            private_key_env_var: Name of environment variable containing the
                private key. Defaults to 'PRIVATE_KEY'.
        """
        self.api_key = api_key
        self.base_url = "https://api.jup.ag" if api_key else "https://lite-api.jup.ag"
        self.private_key_env_var = private_key_env_var

    def _get_headers(self) -> dict[str, str]:
        """
        Get headers for HTTP requests.

        Note: Content-Type header is automatically set by curl_cffi when using
        the json= parameter for POST requests, so it's not included here.

        Returns:
            Dict containing headers with Accept and optional API key.
        """
        headers = {
            "Accept": "application/json",
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    def _load_private_key_bytes(self) -> bytes:
        """
        Loads the private key from the environment variable as base58 or uint8 array.

        Returns:
            bytes: The private key as bytes.

        Raises:
            JupiterValidationError: If the private key is missing, empty, or invalid.
        """
        pk_raw = os.getenv(self.private_key_env_var, "")

        if not pk_raw:
            raise JupiterValidationError(
                f"Private key not found in environment variable '{self.private_key_env_var}'",
                field=self.private_key_env_var,
            )

        pk_raw = pk_raw.strip()

        if not pk_raw:
            raise JupiterValidationError(
                f"Private key is empty in environment variable '{self.private_key_env_var}'",
                field=self.private_key_env_var,
                value="",
            )

        # Handle uint8 array format [1, 2, 3, ...]
        if pk_raw.startswith("[") and pk_raw.endswith("]"):
            try:
                arr = json.loads(pk_raw)
                if not isinstance(arr, list):
                    raise JupiterValidationError(
                        "Private key uint8 array must be a list",
                        field=self.private_key_env_var,
                        value=type(arr).__name__,
                    )

                if not arr:
                    raise JupiterValidationError(
                        "Private key uint8 array cannot be empty", field=self.private_key_env_var, value=arr
                    )

                if not all(isinstance(x, int) and 0 <= x <= 255 for x in arr):
                    invalid_values = [x for x in arr if not isinstance(x, int) or not (0 <= x <= 255)]
                    raise JupiterValidationError(
                        f"Private key uint8 array contains invalid values: {invalid_values[:5]}...",
                        field=self.private_key_env_var,
                        value=invalid_values[:5],
                    )

                return bytes(arr)

            except json.JSONDecodeError as e:
                raise JupiterValidationError(
                    f"Invalid JSON format in private key uint8 array: {e!s}",
                    field=self.private_key_env_var,
                    value=pk_raw[:50] + "..." if len(pk_raw) > 50 else pk_raw,
                ) from e
            except JupiterValidationError:
                # Re-raise our custom validation errors
                raise
            except Exception as e:
                raise JupiterValidationError(
                    f"Failed to parse private key uint8 array: {e!s}", field=self.private_key_env_var
                ) from e

        # Handle base58 format
        try:
            decoded = base58.b58decode(pk_raw)
            if len(decoded) == 0:
                raise JupiterValidationError(
                    "Private key base58 decoded to empty bytes",
                    field=self.private_key_env_var,
                    value=pk_raw[:20] + "..." if len(pk_raw) > 20 else pk_raw,
                )
            return decoded
        except Exception as e:
            raise JupiterValidationError(
                f"Invalid base58 private key format: {e!s}",
                field=self.private_key_env_var,
                value=pk_raw[:20] + "..." if len(pk_raw) > 20 else pk_raw,
            ) from e

    def get_public_key(self) -> str:
        """
        Get the public key from the loaded private key.

        Returns:
            Public key as a base58-encoded string.
        """
        wallet = Keypair.from_bytes(self._load_private_key_bytes())
        return str(wallet.pubkey())

    async def get_public_key_async(self) -> str:
        """
        Async wrapper for get_public_key().

        Returns:
            Public key as a base58-encoded string.
        """
        return self.get_public_key()

    def _sign_base64_transaction(self, transaction_base64: str) -> VersionedTransaction:
        """
        Sign a base64-encoded transaction.

        Args:
            transaction_base64: Base64-encoded transaction string.

        Returns:
            Signed VersionedTransaction object.

        Raises:
            JupiterValidationError: If transaction_base64 is empty or invalid.
        """
        if not transaction_base64:
            raise JupiterValidationError(
                "Empty transaction data received from API. This usually indicates insufficient balance or an API error.",
                field="transaction",
                value=transaction_base64,
            )

        if not isinstance(transaction_base64, str):
            raise JupiterValidationError(
                "Transaction data must be a string", field="transaction", value=type(transaction_base64).__name__
            )

        try:
            transaction_bytes = base64.b64decode(transaction_base64)
            if len(transaction_bytes) == 0:
                raise JupiterValidationError(
                    "Transaction base64 decoded to empty bytes",
                    field="transaction",
                    value=transaction_base64[:50] + "..." if len(transaction_base64) > 50 else transaction_base64,
                )

            versioned_transaction = VersionedTransaction.from_bytes(transaction_bytes)
            return self._sign_versioned_transaction(versioned_transaction)

        except JupiterValidationError:
            # Re-raise our custom validation errors
            raise
        except Exception as e:
            # Check if it's specifically a base64 decoding error
            error_str = str(e)
            if "base64" in error_str.lower() or "invalid" in error_str.lower():
                raise JupiterValidationError(
                    f"Invalid base64 transaction format: {e!s}",
                    field="transaction",
                    value=transaction_base64[:50] + "..." if len(transaction_base64) > 50 else transaction_base64,
                ) from e
            else:
                raise JupiterValidationError(
                    f"Failed to decode/parse transaction: {e!s}. This usually indicates invalid transaction data from the API.",
                    field="transaction",
                ) from e

    def _sign_versioned_transaction(self, versioned_transaction: VersionedTransaction) -> VersionedTransaction:
        """
        Sign a VersionedTransaction with the loaded private key.

        Args:
            versioned_transaction: VersionedTransaction to sign.

        Returns:
            Signed VersionedTransaction with signature applied.
        """
        wallet = Keypair.from_bytes(self._load_private_key_bytes())
        account_keys = versioned_transaction.message.account_keys
        wallet_index = account_keys.index(wallet.pubkey())

        signers = list(versioned_transaction.signatures)
        signers[wallet_index] = wallet  # type: ignore

        return VersionedTransaction(
            versioned_transaction.message,
            signers,  # type: ignore
        )

    def _serialize_versioned_transaction(self, versioned_transaction: VersionedTransaction) -> str:
        """
        Serialize a VersionedTransaction to base64 string.

        Args:
            versioned_transaction: VersionedTransaction to serialize.

        Returns:
            Base64-encoded string representation of the transaction.
        """
        return base64.b64encode(bytes(versioned_transaction)).decode("utf-8")


class JupiterClient(_CoreJupiterClient):
    """
    The synchronous client for interacting with the Jupiter API.
    Powered by curl_cffi.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        private_key_env_var: str = "PRIVATE_KEY",
        client_kwargs: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize the synchronous Jupiter client.

        Args:
            api_key: Optional API key for enhanced access to Jupiter API.
            private_key_env_var: Name of environment variable containing the
                private key.
            client_kwargs: Optional kwargs to pass to curl_cffi Session.
                Common options include 'proxies', 'timeout'.
        """
        super().__init__(api_key, private_key_env_var)
        kwargs = client_kwargs or {}
        self.client = requests.Session(**kwargs)

    def close(self) -> None:
        """
        Close the underlying HTTP session.

        Always call this method when done to properly cleanup resources.
        """
        self.client.close()


class AsyncJupiterClient(_CoreJupiterClient):
    """
    The asynchronous client for interacting with the Jupiter API.
    Powered by curl_cffi.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        private_key_env_var: str = "PRIVATE_KEY",
        client_kwargs: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize the asynchronous Jupiter client.

        Args:
            api_key: Optional API key for enhanced access to Jupiter API.
            private_key_env_var: Name of environment variable containing the
                private key.
            client_kwargs: Optional kwargs to pass to curl_cffi AsyncSession.
                Common options include 'proxies', 'timeout'.
        """
        super().__init__(api_key, private_key_env_var)
        kwargs = client_kwargs or {}
        self.client = AsyncSession(**kwargs)

    async def close(self) -> None:
        """
        Close the underlying HTTP session.

        Always call this method when done to properly cleanup resources.
        """
        await self.client.close()

    # Override get_public_key for async context consistency
    async def get_public_key(self) -> str:  # type: ignore[override]
        """
        Get the public key from the loaded private key.

        Returns:
            Public key as a base58-encoded string.
        """
        return super().get_public_key()
