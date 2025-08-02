"""A module to calculate cash flow
"""

from pydantic import BaseModel
from pydantic import PositiveInt


def compound_future(
    present_value: float, interest_rate: float, n_years: int
) -> float:
    return present_value * (1 + interest_rate) ** n_years


def compound_present(
    future_value: float, interest_rate: float, n_years: int
) -> float:
    return future_value / (1 + interest_rate) ** n_years


class AnnualCashFlowItem(BaseModel):
    """
    Example
    -------
    >>> ci = AnnualCashFlowItem(0, -1000, 'operating cost', 'perpetuity')
    >>> print(ci)
    0 ----------   -1000 ---------- operating cost            perpetuity
    """

    year: PositiveInt
    cf: float
    event: str | None = None
    kind: str | None = (
        None  # TODO: should be enum with "perpetuity" as one of values # noqa: E501
    )

    def __str__(self) -> str:
        s = ""
        s += (f"{self.year} " + "-" * 10).ljust(10) + " "
        s += str(self.cf).rjust(len(str(self.cf)) + 2)
        if self.event:
            s += " " + ("-" * 10 + " " + self.event).rjust(25)
        if self.kind:
            s += " " + (" " * 10 + " " + self.kind).rjust(10)
        return s


class AnnualCashFlow:
    """
    Example:
    >>> cashflow = AnnualCashFlow(
    [(0, -2000), (1, 600), (2, 600), (3, 600), (4, 600)], 0.1
    )
    >>> print(cashflow)
    ============ CASH FLOW ============
    0 ------------------------- -2000
    1 -------------------------   600
    2 -------------------------   600
    3 -------------------------   600
    4 -------------------------   600
    ____________________________________________________________
    Total                        400          INFLOW          2400
                                              OUTFLOW         2000
    ======= DISCOUNTED CASH FLOW =======
    0 -------------------------  -2000.00
    1 -------------------------    545.45
    2 -------------------------    495.87
    3 -------------------------    450.79
    4 -------------------------    409.81
    ______________________________________________________________
    Total                       -98.08          INFLOW       1901.92
                                                OUTFLOW       2000.0
    >>> cashflow.calculate_discounted_cash_flow(rounding=2)
    [
        (0, -2000.0, None),
        (1, 545.45, None),
        (2, 495.87, None),
        (3, 450.79, None),
        (4, 409.81, None),
    ]
    """

    def __init__(
        self,
        cash_flow: (
            list[tuple[int, float]] | list[tuple[int, float, None | str]]
        ),
        time_value_money: float = 0,
    ) -> None:
        self.cash_flow = cash_flow  # type: ignore
        self.time_value_money = time_value_money
        self.discounted_cash_flow = self.calculate_discounted_cash_flow()

    @property
    def cash_flow(
        self,
    ) -> list[tuple[int, float, None | str]]:
        return self._cash_flow

    @cash_flow.setter
    def cash_flow(
        self,
        cash_flow: (
            list[tuple[int, float]] | list[tuple[int, float, str | None]]
        ),
    ) -> None:
        assert type(cash_flow) is list
        for item in cash_flow:
            assert type(item) is tuple
            assert len(item) == 2 or len(item) == 3
        self._cash_flow: list[tuple[int, float, str | None]] = []
        for item in cash_flow:
            if len(item) == 2:
                self._cash_flow.append((item[0], item[1], None))
            elif len(item) == 3:
                self._cash_flow.append((item[0], item[1], item[2]))
            else:
                raise NotImplementedError()

    def netflow(self) -> float:
        return sum(cf for _, cf, _ in self.cash_flow)

    def inflow(self) -> float:
        return sum(
            filter(lambda cf: cf > 0, (cf for _, cf, _ in self._cash_flow))
        )

    def outflow(self) -> float:
        return abs(
            sum(
                filter(lambda cf: cf < 0, (cf for _, cf, _ in self._cash_flow))
            )
        )

    def discounted_netflow(self) -> float:
        return sum(cf for _, cf, _ in self.discounted_cash_flow)

    def discounted_inflow(self) -> float:
        return sum(
            filter(
                lambda cf: cf > 0,
                (cf for _, cf, _ in self.discounted_cash_flow),
            )
        )

    def discounted_outflow(self) -> float:
        return abs(
            sum(
                filter(
                    lambda cf: cf < 0,
                    (cf for _, cf, _ in self.discounted_cash_flow),
                )
            )
        )

    def __str__(self) -> str:
        s = "============ CASH FLOW ============\n"
        max_length = max(len(str(item[1])) for item in self.cash_flow)
        for year, cf, event in self.cash_flow:
            s += (f"{year} " + "-" * 25).ljust(25) + " "
            s += str(cf).rjust(max_length)
            if event:
                s += " " + "-" * 10 + " " + event.rjust(20)
            s += "\n"
        s += "_" * (25 + max_length + 10 + 20) + "\n"
        s += (
            ("Total" + " " * 22).ljust(25)
            + str(self.netflow()).rjust(max_length)
            + " " * 10
            + "INFLOW".ljust(10)
            + str(self.inflow()).rjust(10)
            + "\n"
        )
        s += (
            (" " * (5 + 22 + max_length))
            + " " * 10
            + "OUTFLOW".ljust(10)
            + str(self.outflow()).rjust(10)
            + "\n"
        )
        if self.time_value_money:
            s += "======= DISCOUNTED CASH FLOW =======\n"
            discounted = self.calculate_discounted_cash_flow(rounding=2)
            for year, cf, event in discounted:
                max_length = max(len(str(item[1])) for item in discounted)
                s += (f"{year} " + "-" * 25).ljust(25) + " "
                s += ("{:.2f}".format(cf)).rjust(max_length + 2)
                if event:
                    s += " " + "-" * 10 + " " + event.rjust(20)
                s += "\n"
        s += "_" * (25 + max_length + 10 + 20) + "\n"
        s += (
            ("Total" + " " * 22).ljust(25)
            + str(round(self.discounted_netflow(), 2)).rjust(max_length)
            + " " * 10
            + "INFLOW".ljust(10)
            + str(round(self.discounted_inflow(), 2)).rjust(10)
            + "\n"
        )
        s += (
            (" " * (5 + 22 + max_length))
            + " " * 10
            + "OUTFLOW".ljust(10)
            + str(round(self.discounted_outflow(), 2)).rjust(10)
            + "\n"
        )
        return s[:-1]

    def calculate_discounted_cash_flow(
        self, rounding: int | None = None
    ) -> list[tuple[int, float, None | str]]:
        self.discounted_cash_flow = []
        for year, future_cf, event in self.cash_flow:
            discounted = compound_present(
                future_cf, self.time_value_money, year
            )
            if rounding is None:
                pass
            else:
                assert type(rounding) is int and rounding >= 0
                discounted = round(discounted, rounding)
            self.discounted_cash_flow.append((year, discounted, event))
        return self.discounted_cash_flow

    def npv(self) -> float:
        """
        Example:
        >>> cashflow = AnnualCashFlow([(0, -5), (0, -6), (1, 12)], 0.15)
        >>> npv = cashflow.npv()
        >>> round(npv, 3)
        -0.565
        """
        return sum(cf for _, cf, _ in self.calculate_discounted_cash_flow())


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
