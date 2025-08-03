from typing import Optional

from pyjupiter.models.base_model import BaseModel


class UltraOrderRequest(BaseModel):
    """
    Pydantic model for creating swap orders on Jupiter Ultra API.

    Attributes:
        input_mint: Mint address of the input token.
        output_mint: Mint address of the output token.
        amount: Amount to swap in the smallest unit (e.g., lamports for SOL).
        taker: Optional public key of the taker (usually your wallet address).
        referral_account: Optional referral account address for fee sharing.
        referral_fee: Optional referral fee in basis points (1 bp = 0.01%).
    """

    input_mint: str
    output_mint: str
    amount: int
    taker: Optional[str] = None
    referral_account: Optional[str] = None
    referral_fee: Optional[int] = None
