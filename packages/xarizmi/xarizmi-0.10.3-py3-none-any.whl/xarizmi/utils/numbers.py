import numpy as np


def round_to_significant_digit(value: int | float) -> float:
    """
    Rounds the number to the nearest significant digit level.

    Parameters:
    value (int/float): The number to round.

    Returns:
    int: The rounded number.
    """
    if value == 0:
        return 0

    # Find the power of 10 of the most significant digit
    power = int(np.floor(np.log10(abs(value))))

    # Scale the value to that level and round it
    scale = 10**power
    rounded_value = round(value / scale) * scale

    return rounded_value  # type: ignore
