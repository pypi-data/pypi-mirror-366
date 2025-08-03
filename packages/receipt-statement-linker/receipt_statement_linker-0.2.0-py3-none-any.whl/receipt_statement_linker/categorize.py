import asyncio
from enum import Enum, StrEnum, auto
import textwrap
import litellm
from typing import Any, Generic, TypeVar

from litellm.types.utils import ModelResponse
from pydantic import BaseModel, create_model, model_serializer

from .receipt import Receipt, ReceiptEntry, TranscribedReceipt
from .statement import Transaction
from .pair import TransactionReceiptPair
from .config import Config

DEFAULT_CATEGORIES = [
    "GROCERIES",
    "EATING_OUT",
    "TRANSPORTATION",
    "HOUSING",
    "HEALTHCARE",
    "PERSONAL_CARE",
    "ENTERTAINMENT",
    "SAVINGS_AND_INVESTMENTS",
    "DEBT_PAYMENT",
    "UTILITIES",
    "MISC",
]


def set_categories_enum(
    classifications_list: list[str] | None = None,
) -> type[StrEnum]:
    return StrEnum("Classifications", classifications_list or DEFAULT_CATEGORIES)


T = TypeVar("T", bound=BaseModel)


class Categorized(BaseModel, Generic[T]):
    content: T
    category: Enum

    # NOTE(Rehan): keep category on same level as content basemodel when dumping
    @model_serializer(mode="plain")
    def _flatten(self) -> dict[str, Any]:
        if isinstance(self.content, BaseModel):
            data: dict[str, Any] = self.content.model_dump()
        else:
            data: dict[str, Any] = {"content": self.content}

        data["category"] = self.category
        return data


class CategorizedReceipt(Receipt):
    items: list[Categorized[ReceiptEntry]]

    @classmethod
    def from_transcribed_receipt(
        cls,
        transcribed_receipt: TranscribedReceipt,
        categorized_entries: list[Categorized[ReceiptEntry]],
    ):
        return cls(
            vendor=transcribed_receipt.vendor,
            datetime=transcribed_receipt.datetime,
            subtotal=transcribed_receipt.subtotal,
            grand_total=transcribed_receipt.grand_total,
            items=categorized_entries,
        )


# TODO(Rehan): wanted to subclass TransactionReceiptPair, but idk it is messy, maybe revisit later
class CategorizedTransactionReceiptPair(BaseModel):
    transaction: Categorized[Transaction]
    receipt: CategorizedReceipt | None

    @classmethod
    def from_transaction_receipt_pair(
        cls,
        transaction: Categorized[Transaction],
        receipt: CategorizedReceipt | None,
    ):
        return cls(transaction=transaction, receipt=receipt)


async def categorize_pairs(
    pairs: list[TransactionReceiptPair], categories_enum: type[Enum]
) -> list[CategorizedTransactionReceiptPair]:
    transactions, receipts = (
        TransactionReceiptPair.extract_transactions(pairs),
        TransactionReceiptPair.extract_receipts(pairs),
    )
    categorized_transactions = await categorize_transactions(
        transactions, categories_enum
    )
    categorized_receipts = await categorize_receipts(receipts, categories_enum)

    return [
        CategorizedTransactionReceiptPair.from_transaction_receipt_pair(
            transaction, receipt
        )
        for transaction, receipt in zip(categorized_transactions, categorized_receipts)
    ]


class PlaceholderEnum(StrEnum):
    TEST = auto()


class Category(BaseModel):
    index: int
    category: Enum


class Categories(BaseModel):
    categories: list[Category]


def get_categories_basemodel(categories_enum: type[Enum]) -> type[Categories]:
    category_basemodel = create_model(
        "Category",
        index=int,
        category=categories_enum,
        __base__=Category,
    )
    return create_model(
        "Categories",
        categories=list[category_basemodel],
        __base__=Categories,
    )


def get_user_notes() -> str:
    return Config.get_config().categorization_notes or ""


def get_statement_categorize_prompt() -> str:
    return textwrap.dedent(
        f"""
        You are an accurate categorizer. You will be provided transactions from a bank statement. You will categorize them based on the JSON schema provided.

        {get_user_notes()}
        """
    ).strip()


async def categorize_transactions(
    transactions: list[Transaction],
    categories_enum: type[Enum],
) -> list[Categorized[Transaction]]:
    categories_basemodel = get_categories_basemodel(categories_enum)
    system_prompt = get_statement_categorize_prompt()
    user_message = "\n\n".join(
        f"<index>\n{i}\n</index>\n<transaction>\n{transaction.model_dump_json()}\n</transaction>"
        for i, transaction in enumerate(transactions, start=1)
    )
    messages: list[dict] = [
        {"content": system_prompt, "role": "system"},
        {"role": "user", "content": user_message},
    ]
    response = await litellm.acompletion(
        model=Config.get_config().categorization_model,
        messages=messages,
        response_format=categories_basemodel,
        temperature=0,
    )
    assert isinstance(response, ModelResponse)
    assert isinstance(response.choices[0], litellm.Choices)
    assert response.choices[0].message.content is not None

    validated_categories = categories_basemodel.model_validate_json(
        response.choices[0].message.content
    )
    return [
        Categorized(content=transaction, category=category.category)
        for transaction, category in zip(transactions, validated_categories.categories)
    ]


def get_receipt_categorize_prompt() -> str:
    return textwrap.dedent(
        f"""
        You are an accurate categorizer. You will be provided receipt entries. You will categorize them based on the JSON schema provided.

        {get_user_notes()}
        """
    ).strip()


async def categorize_receipts(
    receipts: list[TranscribedReceipt | None], categories_enum: type[Enum]
) -> list[CategorizedReceipt | None]:
    categories_basemodel = get_categories_basemodel(categories_enum)
    return await asyncio.gather(
        *(categorize_receipt(receipt, categories_basemodel) for receipt in receipts)
    )


async def categorize_receipt(
    receipt: TranscribedReceipt | None, categories_basemodel: type[Categories]
) -> CategorizedReceipt | None:
    if receipt is None:
        return None

    system_prompt = get_receipt_categorize_prompt()
    receipt_input = [
        f"<index>\n{i}\n</index>\n<vendor>\n{receipt.vendor}\n</vendor>\n<receipt_entry>\n{receipt_entry.model_dump_json()}\n</receipt_entry>"
        for i, receipt_entry in enumerate(receipt.items, start=1)
    ]
    user_message = "\n\n".join(
        receipt_str for receipt_str in receipt_input if receipt_str
    )
    messages: list[dict] = [
        {"content": system_prompt, "role": "system"},
        {"role": "user", "content": user_message},
    ]
    response = await litellm.acompletion(
        model=Config.get_config().categorization_model,
        messages=messages,
        response_format=categories_basemodel,
        temperature=0,
    )
    assert isinstance(response, ModelResponse)
    assert isinstance(response.choices[0], litellm.Choices)
    assert response.choices[0].message.content is not None
    validated_categories = categories_basemodel.model_validate_json(
        response.choices[0].message.content
    )

    categorized_entries = [
        Categorized(content=item, category=category.category)
        for item, category in zip(receipt.items, validated_categories.categories)
    ]

    return CategorizedReceipt.from_transcribed_receipt(receipt, categorized_entries)
