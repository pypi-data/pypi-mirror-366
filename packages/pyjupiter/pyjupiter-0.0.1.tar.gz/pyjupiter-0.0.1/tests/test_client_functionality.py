from unittest.mock import AsyncMock, Mock, patch

import pytest
from utils import load_environment

from pyjupiter.clients.ultra_api_client import AsyncUltraApiClient, UltraApiClient
from pyjupiter.models.ultra_api.ultra_order_request_model import UltraOrderRequest


def test_sync_client_initialization():
    """Test sync client can be initialized properly"""
    load_environment()
    client = UltraApiClient()
    assert client is not None
    assert client.base_url == "https://lite-api.jup.ag"

    # Test with API key
    client_with_key = UltraApiClient(api_key="test_key")
    assert client_with_key.base_url == "https://api.jup.ag"

    client.close()
    client_with_key.close()


@pytest.mark.asyncio
async def test_async_client_initialization():
    """Test async client can be initialized properly"""
    load_environment()
    client = AsyncUltraApiClient()
    assert client is not None
    assert client.base_url == "https://lite-api.jup.ag"

    # Test with API key
    client_with_key = AsyncUltraApiClient(api_key="test_key")
    assert client_with_key.base_url == "https://api.jup.ag"

    await client.close()
    await client_with_key.close()


@pytest.mark.requires_private_key
def test_public_key_retrieval():
    """Test public key retrieval from private key"""
    load_environment()
    client = UltraApiClient()

    public_key = client.get_public_key()
    assert public_key is not None
    assert isinstance(public_key, str)
    assert len(public_key) > 0

    client.close()


@pytest.mark.requires_private_key
@pytest.mark.asyncio
async def test_async_public_key_retrieval():
    """Test async public key retrieval"""
    load_environment()
    client = AsyncUltraApiClient()

    public_key = await client.get_public_key()
    assert public_key is not None
    assert isinstance(public_key, str)
    assert len(public_key) > 0

    await client.close()


def test_order_request_model():
    """Test UltraOrderRequest model creation"""
    order = UltraOrderRequest(
        input_mint="So11111111111111111111111111111111111111112",
        output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        amount=10000000,
        taker="CzieXbdjF4suiEBe6rQEgiz8phk6v3fVHndMn1sYgmCv",
    )

    assert order.input_mint == "So11111111111111111111111111111111111111112"
    assert order.output_mint == "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    assert order.amount == 10000000
    assert order.taker == "CzieXbdjF4suiEBe6rQEgiz8phk6v3fVHndMn1sYgmCv"

    # Test dict conversion
    order_dict = order.to_dict()
    assert "inputMint" in order_dict
    assert "outputMint" in order_dict
    assert "amount" in order_dict
    assert "taker" in order_dict


@patch("curl_cffi.requests.Session.get")
def test_sync_balances_mock(mock_get):
    """Test sync balances method with mocked response"""
    load_environment()
    client = UltraApiClient()

    # Mock response
    mock_response = Mock()
    mock_response.json.return_value = {
        "SOL": {
            "amount": "100000000",
            "uiAmount": 0.1,
            "slot": 123456,
            "isFrozen": False,
        }
    }
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    # Test balances
    address = "CzieXbdjF4suiEBe6rQEgiz8phk6v3fVHndMn1sYgmCv"
    balances = client.balances(address)

    assert "SOL" in balances
    assert balances["SOL"]["amount"] == "100000000"
    assert balances["SOL"]["uiAmount"] == 0.1

    client.close()


@pytest.mark.asyncio
async def test_async_balances_mock():
    """Test async balances method with mocked response"""
    load_environment()
    client = AsyncUltraApiClient()

    # Mock the async get method
    mock_response = Mock()
    mock_response.json.return_value = {
        "SOL": {
            "amount": "100000000",
            "uiAmount": 0.1,
            "slot": 123456,
            "isFrozen": False,
        }
    }
    mock_response.raise_for_status = Mock()

    with patch.object(client.client, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        # Test balances
        address = "CzieXbdjF4suiEBe6rQEgiz8phk6v3fVHndMn1sYgmCv"
        balances = await client.balances(address)

        assert "SOL" in balances
        assert balances["SOL"]["amount"] == "100000000"
        assert balances["SOL"]["uiAmount"] == 0.1

    await client.close()
