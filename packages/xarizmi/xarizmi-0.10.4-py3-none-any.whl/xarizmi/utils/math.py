from math import inf


def divide_with_no_zero_division_error(
    num: float | int, den: float | int
) -> float:
    try:
        return float(num) / float(den)
    except ZeroDivisionError:
        return inf
