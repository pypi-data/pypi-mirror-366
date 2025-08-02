import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from talib import abstract

from xarizmi.candlestick import CandlestickChart
from xarizmi.utils.extremums import find_local_maxima_of_maxima_indexes
from xarizmi.utils.extremums import find_local_minima_of_minima_indexes
from xarizmi.utils.plot.timeseries.lineplot import TimeSeriesLinePlot


class OBVIndicator:

    def __init__(
        self, candlestick_chart: CandlestickChart, volume: str = "volume"
    ) -> None:
        self.candlestick_chart = candlestick_chart
        self.volume = volume
        self.indicator_data: None | list[float] = None

    def compute(self) -> list[float]:
        close = np.array(
            [candle.close for candle in self.candlestick_chart.candles]
        ).astype(np.float64)
        if self.volume == "volume":
            volume = np.array(
                [candle.volume for candle in self.candlestick_chart.candles]
            ).astype(np.float64)
        elif self.volume == "amount":
            volume = np.array(
                [candle.amount for candle in self.candlestick_chart.candles]
            ).astype(np.float64)
        self.indicator_data = abstract.OBV(close, volume).tolist()
        return self.indicator_data  # type: ignore

    def compute_local_minimas(self) -> list[int]:
        if self.indicator_data is not None:
            local_minima_indexes = find_local_minima_of_minima_indexes(
                self.indicator_data
            )
            return local_minima_indexes
        else:
            return []

    def compute_local_maximas(self) -> list[int]:
        if self.indicator_data is not None:
            local_maxima_indexes = find_local_maxima_of_maxima_indexes(
                self.indicator_data
            )
            return local_maxima_indexes
        else:
            return []

    def plot(
        self,
        fig_size: tuple[int, int] = (10, 6),
        save_path: str | None = None,
        color: str = "blue",
    ) -> tuple[Figure, Axes]:
        if self.indicator_data is None:
            raise RuntimeError("No data to plot")
        plot = TimeSeriesLinePlot(fig_size=fig_size, color=color)
        dates_data = [
            candle.datetime for candle in self.candlestick_chart.candles
        ]
        plot.plot_main_data(data=self.indicator_data, dates_data=dates_data)

        # local minimas added to plot
        local_minima_indexes = self.compute_local_minimas()
        plot.highlight_points(
            data=[self.indicator_data[i] for i in local_minima_indexes],
            dates_data=[dates_data[i] for i in local_minima_indexes],
            color="green",
        )
        # local maximas added to plot
        local_maxima_indexes = self.compute_local_maximas()
        plot.highlight_points(
            data=[self.indicator_data[i] for i in local_maxima_indexes],
            dates_data=[dates_data[i] for i in local_maxima_indexes],
            color="red",
        )
        if save_path is None:
            plot.show()
        else:
            plot.save(save_path=save_path)

        return plot.fig, plot.ax
