from __future__ import annotations
from pydantic import BaseModel

from .receipt import TranscribedReceipt

from .statement import Transaction


class TransactionReceiptPair(BaseModel):
    transaction: Transaction
    receipt: TranscribedReceipt | None

    @staticmethod
    def extract_transactions(pairs: list[TransactionReceiptPair]) -> list[Transaction]:
        return [pair.transaction for pair in pairs]

    @staticmethod
    def extract_receipts(
        pairs: list[TransactionReceiptPair],
    ) -> list[TranscribedReceipt | None]:
        return [pair.receipt for pair in pairs]

    @classmethod
    def from_transaction_receipt_pair(
        cls, transaction: Transaction, receipt: TranscribedReceipt
    ):
        return cls(transaction=transaction, receipt=receipt)
