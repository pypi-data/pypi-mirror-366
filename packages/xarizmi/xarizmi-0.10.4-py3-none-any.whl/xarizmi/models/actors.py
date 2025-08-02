from pydantic import BaseModel
from pydantic import NonNegativeFloat


class Actor(BaseModel):
    """Actor is base class for actors that are involved in the market."""

    asset: NonNegativeFloat = 0

    def _check_funds_is_non_negative(self, funds: float) -> None:
        if funds < 0:
            raise ValueError(f"The given funds '{funds}' is not non-negative")

    def add_funds(self, funds: float) -> None:
        self._check_funds_is_non_negative(funds=funds)
        self.asset += funds

    def withdraw_funds(self, funds: float) -> None:
        self._check_funds_is_non_negative(funds=funds)
        self.asset -= min(funds, self.asset)


class ExchangeActor(Actor):
    """ExchangeActor is an actor that plays the role of Exchange.

    Exchanges usually have a lot of money and assets. They get fee
    per trader and they have the advantage of knowing the orders of
    other actors who use their platform to trade or invest.

    They also have a lot of money and they can manipulate market in
    good or bad ways.
    """


class TraderActor(Actor):
    """A person who is a trader in the market.
    They buy and sell continuously and they hold securities for a
    short period of time.
    """


class InvestorActor(Actor):
    """InvestorActor holds securities for a long time."""
