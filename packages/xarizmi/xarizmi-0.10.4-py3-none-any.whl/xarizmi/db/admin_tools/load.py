import json
import pathlib
from pathlib import Path
from typing import Callable

from sqlalchemy.orm import Session

from xarizmi.candlestick import Candlestick
from xarizmi.candlestick import CandlestickList
from xarizmi.db.actions.candlestick import upsert_candlestick
from xarizmi.db.actions.exchange import bulk_upsert_exchanges
from xarizmi.db.actions.symbol import bulk_upsert_symbols
from xarizmi.db.actions.symbol import get_symbol
from xarizmi.models.exchange import Exchange
from xarizmi.models.exchange import ExchangeList
from xarizmi.models.symbol import Symbol
from xarizmi.models.symbol import SymbolList


def list_files_with_prefix(
    parent_dir: str | pathlib.Path, file_prefix: str
) -> list[Path]:
    if isinstance(parent_dir, str):
        parent_dir = Path(parent_dir)

    if not parent_dir.is_dir():
        raise ValueError(f"The directory {parent_dir} does not exist.")

    # List all files in the directory that start with the given prefix
    files = [
        file
        for file in parent_dir.iterdir()
        if file.is_file() and file.name.startswith(file_prefix)
    ]

    return files


def load_pydantic_model_from_db_model_exported_json_file(
    parent_dir: pathlib.Path,
    converter_function: Callable,
    file_prefix: str = "xarizmi_exchange_",
    transformer: Callable | None = None,
    insert_in_db: bool = False,
) -> list[Exchange]:
    files = list_files_with_prefix(
        parent_dir=parent_dir, file_prefix=file_prefix
    )
    for filepath in files:
        with open(filepath) as f:
            data = json.load(f)

        if transformer is not None:
            data = map(transformer, data)
        pydantic_items_wrapper = converter_function(items=data)
        yield pydantic_items_wrapper.items


def load_pydantic_exchange_model_from_db_model_exported_json_file(
    parent_dir,
    file_prefix: str = "xarizmi_exchange_",
    insert_in_db: bool = False,
    session: None | Session = None,
) -> list[Exchange]:
    generator = load_pydantic_model_from_db_model_exported_json_file(
        parent_dir, ExchangeList, file_prefix
    )
    exchanges = []
    for items in generator:
        exchanges += items
    if insert_in_db is True:
        if session is None:
            raise RuntimeError("Session is not provided!")
        bulk_upsert_exchanges(exchanges, session=session)
    return exchanges


def load_pydantic_symbol_model_from_db_model_exported_json_file(
    parent_dir,
    file_prefix: str = "xarizmi_symbol_",
    insert_in_db: bool = False,
    session: None | Session = None,
) -> list[Symbol]:

    def transformer(symbol_item: dict[str, str]) -> dict[str, str]:
        symbol_item["exchange"] = symbol_item["exchange_name"]
        return symbol_item

    generator = load_pydantic_model_from_db_model_exported_json_file(
        parent_dir,
        SymbolList.build,
        file_prefix,
        transformer=transformer,
    )
    symbols = []
    for items in generator:
        symbols += items
    if insert_in_db is True:
        bulk_upsert_symbols(symbols, session=session)
    return symbols


def load_pydantic_candlestick_model_from_db_model_exported_json_file(
    parent_dir: str,
    file_prefix: str = "xarizmi_candlestick_",
    insert_in_db: bool = False,
    session: None | Session = None,
    keep_in_memory: bool = False,
) -> list[Candlestick]:

    def transformer(item: dict[str, str]) -> dict[str, str]:

        item["symbol"] = Symbol.build(
            base_currency=item["base_currency"],
            quote_currency=item["quote_currency"],
            fee_currency=item["fee_currency"],
            exchange=item["exchange_name"],
        )

        item["exchange"] = Exchange(name=item["exchange_name"])

        # interval type
        if item["interval_type"] == "MIN_1":
            item["interval_type"] = "1min"
        if item["interval_type"] == "MIN_3":
            item["interval_type"] = "3min"
        if item["interval_type"] == "MIN_5":
            item["interval_type"] = "5min"
        if item["interval_type"] == "MIN_15":
            item["interval_type"] = "15min"
        if item["interval_type"] == "MIN_30":
            item["interval_type"] = "30min"
        if item["interval_type"] == "HOUR_1":
            item["interval_type"] = "1hour"
        if item["interval_type"] == "HOUR_2":
            item["interval_type"] = "2hour"
        if item["interval_type"] == "HOUR_3":
            item["interval_type"] = "3hour"
        if item["interval_type"] == "HOUR_4":
            item["interval_type"] = "4hour"
        if item["interval_type"] == "HOUR_6":
            item["interval_type"] = "6hour"
        if item["interval_type"] == "HOUR_8":
            item["interval_type"] = "8hour"
        if item["interval_type"] == "HOUR_12":
            item["interval_type"] = "12hour"
        if item["interval_type"] == "DAY_1":
            item["interval_type"] = "1day"
        if item["interval_type"] == "DAY_7":
            item["interval_type"] = "7day"
        if item["interval_type"] == "DAY_14":
            item["interval_type"] = "14day"
        if item["interval_type"] == "WEEK_1":
            item["interval_type"] = "7day"
        if item["interval_type"] == "WEEK_2":
            item["interval_type"] = "14day"
        if item["interval_type"] == "MONTH_1":
            item["interval_type"] = "1month"
        return item

    candlesticks = []
    generator = load_pydantic_model_from_db_model_exported_json_file(
        parent_dir,
        CandlestickList,
        file_prefix,
        transformer=transformer,
    )
    cached_symbol_ids: dict[Symbol, int] = {}

    for items in generator:
        if keep_in_memory is True:
            candlesticks += items
        if insert_in_db is True:
            for candlestick in items:
                symbol_id = cached_symbol_ids.get(candlestick.symbol, None)
                if symbol_id is None:
                    symbol_id = get_symbol(
                        symbol=candlestick.symbol, session=session
                    ).id
                    cached_symbol_ids[candlestick.symbol] = symbol_id
                upsert_candlestick(
                    candlestick=candlestick,
                    symbol_id=symbol_id,
                    session=session,
                )
        print("Batch of candlestick items inserted into db ...")

    return candlesticks
