from pydantic import BaseModel
from datetime import datetime


class Transaction(BaseModel):
    name: str
    datetime: datetime
    withdrawl_amount: float | None
    deposit_amount: float | None


class TranscribedStatement(BaseModel):
    opening_balance: float | None
    transactions: list[Transaction]
    closing_balance: float | None


class TranscribedStatements(BaseModel):
    transcribed_statements: list[TranscribedStatement]
