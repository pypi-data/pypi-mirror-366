# Download sample data for several stocks traded in Toronto Stock Exchange data

import os
import pathlib

from xarizmi.opendata.yahoo_finance import YahooFinanceDailyDataClient

SYMBOLS_LIST: list[str] = [
    "T.TO",
    "SHOP.TO",
    "CNR.TO",
    "CNQ.TO",
    "ENB.TO",
    "AC.TO",
    "OTEX.TO",
    "TRP.TO",
    "TFII.TO",
    "LSPD.TO",
]


def setup_data_directory() -> pathlib.Path:

    data_directory = (
        pathlib.Path(".")
        / "data"
        # / datetime.date.today().strftime("%Y-%m-%d")
    )
    if not data_directory.exists():
        data_directory.mkdir(parents=True)

    return data_directory


def download_daily_symbols(parent_directory: pathlib.Path) -> None:
    for symbol in SYMBOLS_LIST:
        YahooFinanceDailyDataClient.download_full_data(
            symbol=symbol,
            filepath=os.path.join(parent_directory, symbol + ".json"),
        )


def main() -> None:
    data_directory = setup_data_directory()
    download_daily_symbols(data_directory)
