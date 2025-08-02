from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure


class TimeSeriesLinePlot:

    def __init__(
        self,
        fig_size: tuple[int, int] = (10, 6),
        save_path: str | None = None,
        label: str = "",
        xlabel: str = "",
        ylabel: str = "",
        title: str = "",
        color: str = "blue",
    ) -> None:
        self.fig_size = fig_size
        self.save_path = save_path
        self.label = label
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.title = title
        self.color = color
        self.fig, self.ax = plt.subplots(1, 1, figsize=self.fig_size)

    def plot_main_data(
        self, data: list[float], dates_data: list[datetime | None]
    ) -> tuple[Figure, Axes]:
        if any(value is None for value in dates_data):
            self.ax.plot(data, label=self.label, color=self.color)
        else:
            self.ax.plot(
                dates_data,  # type: ignore
                data,
                label=self.label,
                color=self.color,
            )

        self.ax.set_title(self.title)
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
        self.ax.legend()
        plt.grid(True)
        return self.fig, self.ax

    def highlight_points(
        self,
        data: list[float],
        dates_data: list[pd.Timestamp | datetime | None],
        color: str = "r",
        marker: str = "o",
        s: float = 100,
        label: str | None = None,
    ) -> tuple[Figure, Axes]:
        self.ax.scatter(
            dates_data,  # type: ignore
            data,
            color=color,
            marker=marker,
            s=s,
            label=label,
        )
        return self.fig, self.ax

    def save(self, save_path: str | None = None) -> None:
        if save_path:
            self.fig.savefig(save_path)
        elif self.save_path:
            self.fig.savefig(self.save_path)

    def show(self) -> None:
        plt.show()
