from litellm.types.utils import ModelResponse
import mimetypes

from .config import Config

from .pair import TransactionReceiptPair

from .statement import (
    TranscribedStatements,
)
from .receipt import FileInput, TranscribedReceipt, TranscribedReceipts
import textwrap
import litellm


litellm.enable_json_schema_validation


# TODO: use enum and dispatcher to specify extractor?
async def receipts_extract(receipts: list[FileInput]) -> TranscribedReceipts:
    return await receipt_to_json(receipts)


def get_mimetype(filepath: str) -> str | None:
    mime, _ = mimetypes.guess_type(filepath)
    return mime


async def receipt_to_json(receipts: list[FileInput]) -> TranscribedReceipts:
    system_prompt = textwrap.dedent(
        """
        You are an accurate receipt transcriber. You will be given image(s) of receipt(s). You will convert it to JSON output based on the schema provided.

        NOTES:
            - Ensure your datetime value is correct and in ISO 8601 format (YYYY-MM-DD HH:MM:SS.sssZ)
            - Item name is to be just the name. Do not include quantity in the name. Quantity has its own field.
        """
    ).strip()

    image_mimetypes = [get_mimetype(receipt.filepath) for receipt in receipts]
    for image_mimetype, receipt in zip(image_mimetypes, receipts):
        if not image_mimetype:
            raise ValueError(f"{receipt.filepath} does not have valid image mimetype")
    receipts_content = [
        {
            "type": "image_url",
            "image_url": {"url": f"data:{image_mimetype};base64,{receipt.b64}"},
        }
        for receipt, image_mimetype in zip(receipts, image_mimetypes)
    ]

    messages: list[dict] = [
        {"content": system_prompt, "role": "system"},
        {"role": "user", "content": receipts_content},
    ]

    response = await litellm.acompletion(
        model=Config.get_config().transcription_model,
        messages=messages,
        response_format=TranscribedReceipts,
        temperature=0,
    )

    # NOTE(Rehan):is there a better way to work around this for type checking? or is this just an unfortunate design decision by litellm??
    # response can be ModelResponse or CustomStreamWrapper, latter doesn't have `choices` field...
    assert isinstance(response, ModelResponse)
    assert isinstance(response.choices[0], litellm.Choices)
    assert response.choices[0].message.content is not None

    return TranscribedReceipts.model_validate_json(response.choices[0].message.content)


async def statements_extract(statements: list[FileInput]) -> TranscribedStatements:
    return await statement_to_json(statements)


async def statement_to_json(statements: list[FileInput]) -> TranscribedStatements:
    system_prompt = textwrap.dedent(
        """
        You are an accurate bank statement transcriber. You will be given bank statement(s). You will convert it to JSON output based on the schema provided.

        NOTES:
            - Ensure your datetime value is correct and in ISO 8601 format (YYYY-MM-DD HH:MM:SS.sssZ).
            - Do not include opening and closing balances in transactions. They belong in their respective fields.
        """
    ).strip()
    statement_content = [
        {
            "type": "image_url",
            "image_url": {"url": f"data:application/pdf;base64,{statement.b64}"},
        }
        for statement in statements
    ]

    messages: list[dict] = [
        {"content": system_prompt, "role": "system"},
        {"role": "user", "content": statement_content},
    ]
    response = await litellm.acompletion(
        model=Config.get_config().transcription_model,
        messages=messages,
        response_format=TranscribedStatements,
        temperature=0,
    )

    # COPYPASTA: receipt_to_json
    # NOTE(Rehan):is there a better way to work around this for type checking? or is this just an unfortunate design decision by litellm??
    # response can be ModelResponse or CustomStreamWrapper, latter doesn't have `choices` field...
    assert isinstance(response, ModelResponse)
    assert isinstance(response.choices[0], litellm.Choices)
    assert response.choices[0].message.content is not None

    return TranscribedStatements.model_validate_json(
        response.choices[0].message.content
    )


async def merge_statements_receipts(
    statements: TranscribedStatements, receipts: TranscribedReceipts
) -> list[TransactionReceiptPair]:
    # plan:
    # - match on price since likelihood of price matching exactly is low
    # - check if vendor match
    #   - we can do this the dumb way first (receipt vendor in )
    pairs: list[TransactionReceiptPair] = []
    receipts_copy = receipts.model_copy(deep=True)

    for statement in statements.transcribed_statements:
        for transaction in statement.transactions:
            receipt: TranscribedReceipt | None = None
            price_match_receipts = [
                receipt
                for receipt in receipts_copy.transcribed_receipts
                if receipt.grand_total == transaction.withdrawl_amount
            ]

            if not price_match_receipts:
                receipt = None

            elif len(price_match_receipts) == 1:
                [receipt] = price_match_receipts

            else:
                name_match_receipt: TranscribedReceipt | None = None

                # NOTE(Rehan): if multiple matches, we just hit the first
                for price_match_receipt in price_match_receipts:
                    if await price_match_receipt.vendor_match_transaction_name(
                        transaction
                    ):
                        receipt = price_match_receipt
                        break

            # NOTE(Rehan): Skip cases where no name match
            if receipt:
                receipts_copy.transcribed_receipts.remove(receipt)
            pairs.append(
                TransactionReceiptPair(transaction=transaction, receipt=receipt)
            )

    return pairs
