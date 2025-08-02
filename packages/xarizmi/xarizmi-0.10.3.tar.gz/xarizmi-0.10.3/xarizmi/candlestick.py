from datetime import datetime as dt
from typing import Any

import mplfinance as mpf
import numpy as np
import pandas as pd
from pydantic import BaseModel
from pydantic import NonNegativeFloat

from xarizmi.config import config
from xarizmi.enums import IntervalTypeEnum
from xarizmi.models.exchange import Exchange
from xarizmi.models.symbol import Symbol
from xarizmi.utils.extremums import find_local_maxima_indexes
from xarizmi.utils.extremums import find_local_maxima_of_maxima_indexes
from xarizmi.utils.extremums import find_local_minima_indexes
from xarizmi.utils.extremums import find_local_minima_of_minima_indexes
from xarizmi.utils.extremums import find_local_minima_values
from xarizmi.utils.numbers import round_to_significant_digit


class Candlestick(BaseModel):
    """This class contains basic properties of a candlestick.

    :param close: the closing price for the corresponding time period
    :type close: float
    :param open: the opening price for the corresponding time period
    :type open: float
    :param low: the lowest traded price for the corresponding time period
    :type low: float
    :param high: the highest traded price for the corresponding time period
    :type high: float
    :param volume: the amount of trading volume (width of the candlestick)
    :type volume: float
    :param amount: [amount description?]
    :type amount: float
    :param interval_type: the time period for each candlestick
    :type interval_type: str
    :param symbol: the type of the trade, e.g., "CAD-USD" or "BTC-USDT"
    :type symbol: str
    """

    close: NonNegativeFloat
    open: NonNegativeFloat
    low: NonNegativeFloat
    high: NonNegativeFloat
    volume: NonNegativeFloat
    amount: NonNegativeFloat | None = None
    interval_type: IntervalTypeEnum | None = None
    interval: int | None = None  # interval in seconds
    symbol: Symbol | None = None
    datetime: dt | None = None
    exchange: Exchange | None = None

    @property
    def is_bullish(self) -> bool:
        if self.close >= self.open:
            return True
        else:
            return False

    @property
    def is_bearish(self) -> bool:
        if self.open >= self.close:
            return True
        else:
            return False

    @property
    def range(self) -> float:
        """Range = H - L"""
        return self.high - self.low

    @property
    def intrinsic_range(self) -> float:
        """
        IR = R / L
        """
        if (self.low) == 0:
            return 0
        else:
            return self.range / (self.low)

    @property
    def body(self) -> float:
        """B = O - C"""
        return abs(self.open - self.close)

    @property
    def intrinsic_body(self) -> float:
        """B / R"""
        if self.range == 0:
            return 0
        return self.body / self.range

    @property
    def upper_shadow(self) -> float:
        """US = H - MAX(C, O)"""
        return self.high - max(self.close, self.open)

    @property
    def intrinsic_upper_shadow(self) -> float:
        """US / R"""
        if self.range == 0:
            return 0
        return self.upper_shadow / self.range

    @property
    def lower_shadow(self) -> float:
        """LS = min(C, O) - L"""
        return min(self.close, self.open) - self.low

    @property
    def intrinsic_lower_shadow(self) -> float:
        """LS / R"""
        if self.range == 0:
            return 0
        return self.lower_shadow / self.range

    @property
    def doginess(self) -> float:
        if self.range == 0:
            return 0
        return 1 - self.intrinsic_body

    @property
    def is_doji(self) -> bool:
        if self.range == 0:
            return False
        return self.doginess >= config.DOJINESS_THRESHOLD

    def flatten(self) -> dict[str, Any]:
        if self.symbol is None:
            raise NotImplementedError(
                "flatten method is not implemented for instances with "
                "None value for self.symbol"
            )
        data = self.model_dump()
        del data["symbol"]
        data["base_currency"] = self.symbol.base_currency.name
        data["quote_currency"] = self.symbol.quote_currency.name
        data["exchange"] = (
            self.exchange.name if (self.exchange is not None) else None
        )
        return data


class CandlestickChart(BaseModel):
    candles: list[Candlestick]

    def filter_keep_last_n(
        self, keep_last_n: int | None = None, inplace: bool = False
    ) -> "CandlestickChart":
        if keep_last_n:
            candles = self.candles[-keep_last_n:]
            if inplace is True:
                self.candles = candles
                return self
            else:
                return CandlestickChart(candles=candles)
        return self

    def to_df(self) -> pd.DataFrame:
        df = pd.DataFrame(
            data={
                "open": [candle.open for candle in self.candles],
                "close": [candle.close for candle in self.candles],
                "low": [candle.low for candle in self.candles],
                "high": [candle.high for candle in self.candles],
                "datetime": [candle.datetime for candle in self.candles],
                "volume": [candle.volume for candle in self.candles],
                "amount": [candle.amount for candle in self.candles],
            }
        )
        df.set_index("datetime", inplace=True)
        return df

    def save_simple_plot_no_volume(self, filepath: str) -> None:
        custom_style = mpf.make_mpf_style(  # type: ignore
            base_mpf_style="classic",
            marketcolors=mpf.make_marketcolors(  # type: ignore
                up="green",
                down="red",
                wick="black",
                edge="inherit",
            ),
        )
        mpf.plot(
            self.to_df(),
            type="candle",
            style=custom_style,
            title="Candlestick Chart",
            ylabel="Price",
            savefig="candlestick_chart.svg",
        )

    def plot(self, figsize: tuple[int | float, int | float] = (8, 4)) -> None:

        df = self.to_df()

        mask = np.isin(df.index, df.index[self.get_support_indexes()])
        masked_df = df.copy()
        masked_df[~mask] = np.nan  # Replace rows not in index_list with NaN
        apd1 = mpf.make_addplot(
            masked_df["low"],
            type="scatter",
            color="darkgreen",
            marker="h",
            markersize=20,
            alpha=0.50,
        )
        mask = np.isin(df.index, df.index[self.get_l2_support_indexes()])
        masked_df = df.copy()
        masked_df[~mask] = np.nan  # Replace rows not in index_list with NaN
        apd3 = mpf.make_addplot(
            masked_df["low"],
            type="scatter",
            color="darkgreen",
            marker="s",
            markersize=100,
            alpha=0.5,
        )
        mask = np.isin(df.index, df.index[self.get_resistance_indexes()])
        masked_df = df.copy()
        masked_df[~mask] = np.nan  # Replace rows not in index_list with NaN
        apd2 = mpf.make_addplot(
            masked_df["high"],
            type="scatter",
            color="darkred",
            marker="h",
            markersize=20,
            alpha=0.50,
        )
        mask = np.isin(df.index, df.index[self.get_l2_resistance_indexes()])
        masked_df = df.copy()
        masked_df[~mask] = np.nan  # Replace rows not in index_list with NaN
        apd4 = mpf.make_addplot(
            masked_df["high"],
            type="scatter",
            color="darkred",
            marker="s",
            markersize=100,
            alpha=0.5,
        )
        mpf.plot(
            df,
            figratio=figsize,
            type="candle",
            volume=True,
            # style="yahoo",
            style="classic",
            addplot=[apd1, apd2, apd3, apd4],
        )

    def get_local_minimas(
        self, price_type: str = "low", only_significant_digit: bool = False
    ) -> list[int | float]:
        if price_type not in ["low", "high", "close", "open"]:
            raise ValueError(
                f"The given value for {price_type=}" f" is not valid!"
            )
        values = find_local_minima_values(
            [getattr(candle, price_type) for candle in self.candles]
        )
        if only_significant_digit is True:
            values = [round_to_significant_digit(item) for item in values]
        return values

    def get_support_indexes(self) -> list[int]:
        return find_local_minima_indexes(
            [candle.low for candle in self.candles]
        )

    def get_l2_support_indexes(self) -> list[int]:
        return find_local_minima_of_minima_indexes(
            [candle.low for candle in self.candles]
        )

    def get_resistance_indexes(self) -> list[int]:
        return find_local_maxima_indexes(
            [candle.high for candle in self.candles]
        )

    def get_l2_resistance_indexes(self) -> list[int]:
        return find_local_maxima_of_maxima_indexes(
            [candle.high for candle in self.candles]
        )


class CandlestickList(BaseModel):
    items: list[Candlestick] = []
