from xarizmi.candlestick import CandlestickChart


def example_simple_candlestick_plot_no_volume() -> None:

    candles_data = [
        {
            "datetime": "2024-12-18",
            "open": 100,
            "close": 103,
            "high": 105,
            "low": 98,
            "volume": 1,
        },
        {
            "datetime": "2024-12-19",
            "open": 102,
            "close": 106,
            "high": 107,
            "low": 101,
            "volume": 1,
        },
        {
            "datetime": "2024-12-20",
            "open": 107,
            "close": 103,
            "high": 108,
            "low": 101,
            "volume": 1,
        },
    ]

    candlesticks = CandlestickChart.model_validate({"candles": candles_data})

    candlesticks.save_simple_plot_no_volume("candlestick_chart.svg")


if __name__ == "__main__":
    example_simple_candlestick_plot_no_volume()
