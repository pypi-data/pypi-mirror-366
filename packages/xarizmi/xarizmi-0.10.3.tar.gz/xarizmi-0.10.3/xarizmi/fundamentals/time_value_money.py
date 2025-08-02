"""A module to calculate time value of money
"""


def risk_free_return(
    impatience_to_consume: float,
    inflation: float,
) -> float:
    """Calculates risk free return of time value money.

    Parameters
    ----------
    impatience_to_consume : float
        People tend to prefer consuming now rather than later.
        This is called impatience to consume.
        The other name for this in finance is "pure rate of interest".
        For example, a person might have 2 percent (0.02) Impatience to
        consume which means that he or she expects 2 percent reward in order
        to not consume and invest instead.

    inflation : float
        The inflation as defined in economy which is general progressive
        increase in prices of goods and services in an economy.


    Returns
    -------
    float
        Returns the risk free return


    Example
    -------
    >>> risk_free_return(0.05,0.10)
    0.155

    """
    return (1 + impatience_to_consume) * (1 + inflation) - 1


def time_value_money(
    impatience_to_consume: float,
    inflation: float,
    risk: float,
) -> float:
    """Calculates time value of money.

    Parameters
    ----------
    impatience_to_consume : float
        People tend to prefer consuming now rather than later.
        This is called impatience to consume.
        The other name for this in finance is "pure rate of interest".
        For example, a person might have 2 percent (0.02) Impatience to
        consume which means that he or she expects 2 percent reward in order
        to not consume and invest instead.

    inflation : float
        The inflation as defined in economy which is general progressive
        increase in prices of goods and services in an economy.

    risk : float
        The amount of risk which exists in an investment.


    Returns
    -------
    float
        Returns the time value of money.


    Example
    -------
    >>> round(time_value_money(0.05,0.10,0.045),4)
    0.2
    >>> round(time_value_money(0.02,0.03,0),4)
    0.0506

    """
    return (1 + impatience_to_consume) * (1 + inflation) * (1 + risk) - 1


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
