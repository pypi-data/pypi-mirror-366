from pyjupiter.models.base_model import BaseModel


class UltraExecuteRequest(BaseModel):
    """
    Pydantic model for executing a previously created order.

    Attributes:
        signed_transaction: Base64-encoded signed transaction string.
        request_id: The request ID returned from the order endpoint.
    """

    signed_transaction: str
    request_id: str
