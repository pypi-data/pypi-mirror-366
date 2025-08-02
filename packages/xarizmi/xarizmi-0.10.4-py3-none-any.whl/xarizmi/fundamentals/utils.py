def calculate_return_rate_from_price(
    old_price: float, new_price: float
) -> float:
    return new_price / old_price - 1


def calculate_compound_return_rate(
    *, n_periods: int, return_rate_per_period: float
) -> float:
    return (1 + return_rate_per_period) ** n_periods - 1


def calculate_average_compound_return_rate_per_period(
    *, n_periods: int, total_return_rate: float
) -> float:
    return (1 + total_return_rate) ** (1 / n_periods) - 1  # type: ignore
