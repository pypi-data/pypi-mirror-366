import pytest
from pydantic import ValidationError

from xarizmi.candlestick import Candlestick
from xarizmi.candlestick import CandlestickChart
from xarizmi.config import get_config


class TestCandlestick:
    def test(self) -> None:
        data = {
            "close": 2.5,
            "open": 1,
            "low": 0.5,
            "high": 3,
            "volume": 100,
            "amount": 150,
        }
        candle = Candlestick(**data)
        assert candle.close == 2.5
        assert candle.open == 1
        assert candle.low == 0.5
        assert candle.high == 3
        assert candle.range == 2.5
        assert candle.body == 1.5
        assert candle.is_bearish is False
        assert candle.is_bullish is True
        assert candle.doginess == 1 - (1.5 / 2.5)

        assert candle.model_dump() == pytest.approx(
            {
                "close": 2.5,
                "open": 1,
                "low": 0.5,
                "high": 3,
                "interval_type": None,
                "interval": None,
                "symbol": None,
                "volume": 100,
                "amount": 150,
                "datetime": None,
                "exchange": None,
            }
        )

    def test_flatten(self) -> None:
        data = {
            "close": 2.5,
            "open": 1,
            "low": 0.5,
            "high": 3,
            "volume": 100,
            "amount": 150,
            "exchange": {"name": "BINANCE"},
            "symbol": {
                "base_currency": {"name": "BTC"},
                "quote_currency": {"name": "USDT"},
                "fee_currency": {"name": "USDT"},
                "exchange": {"name": "BINANCE"},
            },
        }
        candle = Candlestick.model_validate(data)

        assert candle.flatten() == pytest.approx(
            {
                "close": 2.5,
                "open": 1,
                "low": 0.5,
                "high": 3,
                "interval_type": None,
                "interval": None,
                "volume": 100,
                "amount": 150,
                "datetime": None,
                "exchange": "BINANCE",
                "base_currency": "BTC",
                "quote_currency": "USDT",
            }
        )

    def test_intrinsic_range(self) -> None:
        zero_data = {
            "close": 0,
            "open": 0,
            "low": 0,
            "high": 0,
            "volume": 0,
            "amount": 0,
        }
        candle = Candlestick(**zero_data)
        assert candle.intrinsic_range == 0
        data = {
            "close": 2.5,
            "open": 1,
            "low": 0.5,
            "high": 3,
            "volume": 100,
            "amount": 150,
        }
        candle = Candlestick(**data)
        assert candle.intrinsic_range == 2.5 / 0.5

    def test_intrinsic_body(self) -> None:
        zero_data = {
            "close": 0,
            "open": 0,
            "low": 0,
            "high": 0,
            "volume": 0,
            "amount": 0,
        }
        candle = Candlestick(**zero_data)
        assert candle.intrinsic_range == 0
        data = {
            "close": 2.5,
            "open": 1,
            "low": 0.5,
            "high": 3,
            "volume": 100,
            "amount": 150,
        }
        candle = Candlestick(**data)
        assert candle.intrinsic_body == 1.5 / 2.5

    def test_intrinsic_upper_shadow(self) -> None:
        zero_data = {
            "close": 0,
            "open": 0,
            "low": 0,
            "high": 0,
            "volume": 0,
            "amount": 0,
        }
        candle = Candlestick(**zero_data)
        assert candle.intrinsic_upper_shadow == 0
        data = {
            "close": 2.5,
            "open": 1,
            "low": 0.5,
            "high": 3,
            "volume": 100,
            "amount": 150,
        }
        candle = Candlestick(**data)
        assert candle.upper_shadow == 0.5
        assert candle.intrinsic_upper_shadow == 0.5 / 2.5

    def test_intrinsic_lower_shadow(self) -> None:
        zero_data = {
            "close": 0,
            "open": 0,
            "low": 0,
            "high": 0,
            "volume": 0,
            "amount": 0,
        }
        candle = Candlestick(**zero_data)
        assert candle.intrinsic_lower_shadow == 0
        data = {
            "close": 2.5,
            "open": 1,
            "low": 0.5,
            "high": 3,
            "volume": 100,
            "amount": 150,
        }
        candle = Candlestick(**data)
        assert candle.lower_shadow == 0.5
        assert candle.intrinsic_lower_shadow == 0.5 / 2.5

    def test_negative_price(self) -> None:
        # Given a data with negative price
        data = {
            "close": -2.5,
            "open": 1,
            "low": 0.5,
            "high": 3,
            "volume": 100,
            "amount": 150,
        }
        # When Candlestick constructor is called
        # Then I should see ValidationError
        with pytest.raises(ValidationError):
            Candlestick(**data)

    def test_is_dogi(self) -> None:
        # Given a data with negative price
        data = {
            "close": 30,
            "open": 20,
            "low": 10,
            "high": 40,
            "volume": 100,
            "amount": 150,
        }
        # When a candlestick with this data is created
        c = Candlestick(**data)
        # Then I should have
        assert c.is_doji is False

        # And when I change the config
        config = get_config()
        config.DOJINESS_THRESHOLD = 0.1
        # When a candlestick with this data is created
        c = Candlestick(**data)
        # Then I should have
        assert c.is_doji is True
        config.reset()

    def test_is_dogi_when_range_is_zero(self) -> None:
        # Given a data with high and low are in same price
        data = {
            "close": 30,
            "open": 30,
            "low": 30,
            "high": 30,
            "volume": 100,
            "amount": 150,
        }
        # When a candlestick with this data is created
        c = Candlestick(**data)
        # Then I should have
        assert c.is_doji is False

    def test_is_doginess_when_range_is_zero(self) -> None:
        # Given a data with high and low are in same price
        data = {
            "close": 30,
            "open": 30,
            "low": 30,
            "high": 30,
            "volume": 100,
            "amount": 150,
        }
        # When a candlestick with this data is created
        c = Candlestick(**data)
        # Then I should have
        assert c.doginess == 0


class TestCandlestickChart:

    def test(self) -> None:
        data = {
            "candles": [
                {
                    "low": 0.61873,
                    "high": 0.727,
                    "close": 0.714,
                    "open": 0.71075,
                    "interval_type": "1week",
                    "interval": 604800,
                    "symbol": None,
                    "volume": 100,
                    "amount": 150,
                    "datetime": None,
                    "exchange": None,
                },
                {
                    "low": 0.65219,
                    "high": 0.75,
                    "close": 0.70238,
                    "open": 0.71075,
                    "interval_type": "1week",
                    "interval": 604800,
                    "symbol": None,
                    "volume": 100,
                    "amount": 150,
                    "datetime": None,
                    "exchange": None,
                },
                {
                    "low": 0.64801,
                    "high": 0.92,
                    "close": 0.8404,
                    "open": 0.70238,
                    "interval_type": "1week",
                    "interval": 604800,
                    "symbol": None,
                    "volume": 100,
                    "amount": 150,
                    "datetime": None,
                    "exchange": None,
                },
            ]
        }

        chart = CandlestickChart(**data)

        assert chart.model_dump() == pytest.approx(data)

    def test_to_df(self) -> None:
        data = {
            "candles": [
                {
                    "low": 0.61873,
                    "high": 0.727,
                    "close": 0.714,
                    "open": 0.71075,
                    "interval_type": "1week",
                    "interval": 604800,
                    "symbol": None,
                    "volume": 100,
                    "amount": 150,
                    "datetime": None,
                },
                {
                    "low": 0.65219,
                    "high": 0.75,
                    "close": 0.70238,
                    "open": 0.71075,
                    "interval_type": "1week",
                    "interval": 604800,
                    "symbol": None,
                    "volume": 100,
                    "amount": 150,
                    "datetime": None,
                },
                {
                    "low": 0.64801,
                    "high": 0.92,
                    "close": 0.8404,
                    "open": 0.70238,
                    "interval_type": "1week",
                    "interval": 604800,
                    "symbol": None,
                    "volume": 100,
                    "amount": 150,
                    "datetime": None,
                },
            ]
        }

        chart = CandlestickChart(**data)

        df = chart.to_df()
        assert df["open"].tolist() == [0.71075, 0.71075, 0.70238]
        assert df["close"].tolist() == [0.714, 0.70238, 0.8404]
        assert df["low"].tolist() == [0.61873, 0.65219, 0.64801]
        assert df["high"].tolist() == [0.727, 0.75, 0.92]

    def test_btc_usdt_monthly_data(
        self, btc_usdt_monthly_data: list[dict[str, int | float]]
    ) -> None:
        # Given dataset of BTC-USDT candlestick data
        # When CandlestickChart is called
        c = CandlestickChart.model_validate({"candles": btc_usdt_monthly_data})
        # Then I should have
        assert len(c.candles) == 80

    def test_get_local_minima_candles(
        self, btc_usdt_monthly_data: list[dict[str, int | float]]
    ) -> None:
        # Given dataset of BTC-USDT candlestick data
        # And a candlestick chart with this data
        c = CandlestickChart.model_validate({"candles": btc_usdt_monthly_data})
        # When CandlestickChart.get_local_minima_candles is called
        values = c.get_local_minimas()
        # Then I should have
        assert len(values) == 17
        assert values[:17] == [
            5005.0,
            5950.0,
            6412.000001,
            5736.812481,
            5865.0,
            3160.000001,
            6437.0,
            3800.0,
            9825.0,
            28801.8,
            32918.7,
            17614.7,
            15473.6,
            19558.1,
            24807.5,
            24901.7,
            56560.0,
        ]

        # And when CandlestickChart.get_local_minima_candles is called
        # with only_significant_digit argument set to True
        values = c.get_local_minimas(only_significant_digit=True)
        # Then I should have
        assert values == [
            5000.0,
            6000.0,
            6000.0,
            6000.0,
            6000.0,
            3000.0,
            6000.0,
            4000.0,
            10000.0,
            30000.0,
            30000.0,
            20000.0,
            20000.0,
            20000.0,
            20000.0,
            20000.0,
            60000.0,
        ]

    def test_get_local_minima_candles_raise_error_for_invalid_argument(
        self, btc_usdt_monthly_data: list[dict[str, int | float]]
    ) -> None:
        # Given dataset of BTC-USDT candlestick data
        # And a candlestick chart with this data
        c = CandlestickChart.model_validate({"candles": btc_usdt_monthly_data})
        # When CandlestickChart.get_local_minima_candles is called with
        # wrong argument
        # Then I should have
        with pytest.raises(ValueError):
            c.get_local_minimas(price_type="DOES_NOT_EXIST")
