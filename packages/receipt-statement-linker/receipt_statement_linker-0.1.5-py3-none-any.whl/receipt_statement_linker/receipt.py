import base64
import litellm
import textwrap
from litellm.types.utils import ModelResponse
from pydantic import BaseModel
from datetime import datetime

from .config import Config

from .statement import Transaction


class ReceiptEntry(BaseModel):
    quantity: int
    name: str
    price: float


class Receipt(BaseModel):
    vendor: str
    datetime: datetime
    subtotal: float
    grand_total: float


# TODO: deal with discrepancies between subtotal and sum of items
# need to think about if we should error, or warn, or something else??
class TranscribedReceipt(Receipt):
    items: list[ReceiptEntry]

    async def vendor_match_transaction_name(self, transaction: Transaction) -> bool:
        system_prompt = textwrap.dedent(
            """
            You are an accurate receipt vendor to statement transaction name matcher. You will be provided a vendor name from a receipt, and a transaction name from a bank statement. You will determine if they refer to the same vendor/merchant. If they do, output "MATCH". If they do not, output "MISMATCH". DO NOT OUTPUT ANYTHING ELSE.
            """
        ).strip()

        user_message = textwrap.dedent(
            f"""
            <receipt_vendor>
            {self.vendor}
            </receipt_vendor>

            <statement_transaction_name>
            {transaction.name}
            </statement_transaction_name>
            """
        ).strip()

        messages: list[dict] = [
            {"content": system_prompt, "role": "system"},
            {"role": "user", "content": user_message},
        ]
        response = await litellm.acompletion(
            model=Config.get_config().matching_model,
            messages=messages,
            temperature=0,
        )

        # COPYPASTA: extract.py
        # COPYPASTA: receipt_to_json
        assert isinstance(response, ModelResponse)
        assert isinstance(response.choices[0], litellm.Choices)
        assert response.choices[0].message.content is not None

        return response.choices[0].message.content.lower() == "match"


class TranscribedReceipts(BaseModel):
    transcribed_receipts: list[TranscribedReceipt]


class FileInput:
    def __init__(self, filepath):
        self._filepath: str = filepath
        self._b64: str | None = None

    @property
    def filepath(self) -> str:
        return self._filepath

    @property
    def b64(self) -> str:
        if not self._b64:
            with open(self._filepath, "rb") as image_file:
                self._b64 = base64.b64encode(image_file.read()).decode()

        return self._b64
