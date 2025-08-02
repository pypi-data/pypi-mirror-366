"""Module for Financial Transactions
"""

import datetime


class Transaction:

    def __init__(
        self,
        ID: str,
        amount: float,
        inflow: bool,
        time: datetime.datetime,
        description: str = "",
        currency_code: str = "USD",
    ) -> None:
        self.ID = ID
        self.amount = amount
        self.inflow = inflow
        self.time = time
        self.description = description
        self.currency_code = currency_code

    @property
    def amount(self) -> float:
        return self._amount

    @amount.setter
    def amount(self, amount: float | int) -> None:
        assert type(amount) is float or type(amount) is int
        assert amount > 0
        self._amount = amount

    @property
    def inflow(self) -> bool:
        return self._inflow

    @inflow.setter
    def inflow(self, inflow: int | float) -> None:
        assert type(inflow) is bool
        self._inflow = inflow

    @property
    def time(self) -> datetime.datetime:
        return self._time

    @time.setter
    def time(self, time: datetime.datetime) -> None:
        assert type(time) is datetime.datetime
        self._time = time
        self._date = time.date()

    @property
    def date(self) -> datetime.date:
        return self._date

    @property
    def currency_code(self) -> str:
        return self._currency_code

    @currency_code.setter
    def currency_code(self, currency_code: str) -> None:
        assert type(currency_code) is str
        assert currency_code in [
            "USD",
            "IRR",
            "AUD",
            "EUR",
        ]
        self._currency_code = currency_code

    def __str__(self) -> str:
        return (
            f"{'+' if self.inflow else '-'}{self.amount:,}"
            " - {self.description}"
        )
