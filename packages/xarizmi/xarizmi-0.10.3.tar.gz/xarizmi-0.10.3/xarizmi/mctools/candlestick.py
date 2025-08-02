import datetime

import numpy as np

from xarizmi.candlestick import Candlestick


def generate_four_random_numbers(
    lower_limit: float = 0, scale: float = 1
) -> list[float]:
    nums = lower_limit + (np.random.random(4) * scale)
    nums.sort()
    return nums.tolist()  # type: ignore


def generate_random_candlestick(
    lower_limit: float = 0,
    scale: float = 1,
    datetime: None | datetime.datetime = None,
) -> Candlestick:
    nums = generate_four_random_numbers(lower_limit=lower_limit, scale=scale)
    return Candlestick(
        close=nums[2],
        open=nums[1],
        low=nums[0],
        high=nums[3],
        volume=np.random.randint(low=100, high=200),
        amount=np.random.randint(low=100, high=200),
        datetime=datetime,
    )


def generate_random_bullish_candlestick(
    lower_limit: float = 0,
    scale: float = 1,
    datetime: datetime.datetime | None = None,
) -> Candlestick:
    nums = generate_four_random_numbers(lower_limit=lower_limit, scale=scale)
    return Candlestick(
        close=nums[2],
        open=nums[1],
        low=nums[0],
        high=nums[3],
        volume=np.random.randint(low=100, high=200),
        amount=np.random.randint(low=100, high=200),
        datetime=datetime,
    )


def generate_random_bearish_candlestick(
    lower_limit: float = 0,
    scale: float = 1,
    datetime: None | datetime.datetime = None,
) -> Candlestick:
    nums = generate_four_random_numbers(lower_limit=lower_limit, scale=scale)
    return Candlestick(
        close=nums[1],
        open=nums[2],
        low=nums[0],
        high=nums[3],
        volume=np.random.randint(low=100, high=200),
        amount=np.random.randint(low=100, high=200),
        datetime=datetime,
    )
