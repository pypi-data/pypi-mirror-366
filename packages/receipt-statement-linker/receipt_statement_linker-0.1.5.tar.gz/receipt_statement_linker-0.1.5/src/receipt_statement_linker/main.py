import argparse
import uuid
import json
import asyncio

from .config import set_logger

from .categorize import categorize_pairs, set_categories_enum
from .extract import merge_statements_receipts, receipts_extract, statements_extract
from .receipt import FileInput


async def main():
    set_logger()
    parser = argparse.ArgumentParser(
        description="Parse receipt images and output data."
    )
    parser.add_argument(
        "--receipt-input", nargs="+", required=True, help="Receipt files to parse"
    )
    parser.add_argument(
        "--statement-input", nargs="+", required=True, help="Statement files to parse"
    )
    parser.add_argument(
        "--receipt-output", required=True, help="Filepath to output JSON receipt data"
    )
    parser.add_argument(
        "--categorize",
        action="store_true",
        help="Turn categorization on",
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        required=False,
        help="List of categories",
    )

    args = parser.parse_args()

    receipt_input_filepaths: list[str] = args.receipt_input
    statement_input_filepaths: list[str] = args.statement_input

    receipts = [FileInput(filepath) for filepath in receipt_input_filepaths]
    receipt_extracts = await receipts_extract(receipts)

    statements = [FileInput(filepath) for filepath in statement_input_filepaths]
    statement_extracts = await statements_extract(statements)

    # merge
    pairs = await merge_statements_receipts(statement_extracts, receipt_extracts)

    if args.categorize:
        pairs = await categorize_pairs(pairs, set_categories_enum(args.categories))

    pairs_json = [json.loads(pair.model_dump_json()) for pair in pairs]
    for pair_json in pairs_json:
        pair_json["id"] = str(uuid.uuid4())

    with open(args.receipt_output, "w") as f:
        json.dump(pairs_json, f, indent=4)


if __name__ == "__main__":
    asyncio.run(main())
