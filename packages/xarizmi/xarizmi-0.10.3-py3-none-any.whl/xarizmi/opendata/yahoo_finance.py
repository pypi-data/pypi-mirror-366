"""A client to download Yahoo Finance data
"""

from typing import Any

import pandas as pd
import yfinance as yf

from xarizmi.candlestick import CandlestickChart


class YahooFinanceDailyDataClient:

    def __init__(
        self,
        symbol: str,
        start_date: str = "1900-01-01",
        end_date: str | None = None,
    ) -> None:
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date

    def extract(
        self,
    ) -> list[dict[str, str | float | pd.Timestamp]] | None:
        stock_data: pd.DataFrame = yf.download(
            self.symbol, start=self.start_date, end=self.end_date
        )

        if stock_data.empty:
            print("Error fetching data for symbol:", self.symbol)
            return None

        # Reset the index to get 'Date' as a column
        stock_data.reset_index(inplace=True)

        return stock_data.to_dict(orient="records")  # type: ignore

    def transform(
        self, data_list: list[dict[str, str | float | pd.Timestamp]]
    ) -> CandlestickChart:
        candles_data = []
        for single_candle_data in data_list:
            temp: dict[str, Any] = {}
            data = single_candle_data.copy()
            for key, value in single_candle_data.items():
                data[key[0]] = value
            temp["open"] = data["Open"]
            temp["high"] = data["High"]
            temp["low"] = data["Low"]
            temp["close"] = data["Close"]
            temp["volume"] = data["Volume"]
            temp["datetime"] = data["Date"].to_pydatetime()  # type: ignore  # noqa:E501
            temp["interval_type"] = "1day"
            temp["symbol"] = {
                "base_currency": {"name": self.symbol},
                "quote_currency": {"name": "CAD"},
                "fee_currency": {"name": "CAD"},
            }
            candles_data.append(temp)
        return CandlestickChart.model_validate({"candles": candles_data})

    def save_file(
        self,
        candlestick_chart: CandlestickChart,
        filepath: str,
        indent: int = 4,
    ) -> None:
        with open(filepath, "w") as f:
            f.write(candlestick_chart.model_dump_json(indent=indent))

    def etl(self, filepath: str) -> CandlestickChart:
        data_list = self.extract()
        if data_list:
            candlestick_chart = self.transform(
                data_list=data_list
            )  # noqa: E501
            self.save_file(
                candlestick_chart=candlestick_chart, filepath=filepath
            )
            return candlestick_chart
        else:
            return CandlestickChart(candles=[])

    @staticmethod
    def download_full_data(symbol: str, filepath: str) -> CandlestickChart:
        client = YahooFinanceDailyDataClient(symbol=symbol)
        candlestick_chart = client.etl(filepath=filepath)
        return candlestick_chart
