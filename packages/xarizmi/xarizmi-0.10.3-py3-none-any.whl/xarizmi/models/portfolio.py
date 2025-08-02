import datetime

from pydantic import BaseModel
from pydantic import field_validator

from xarizmi.utils.math import divide_with_no_zero_division_error

from .symbol import Symbol


class PortfolioItem(BaseModel):
    symbol: Symbol
    market_value: float
    quantity: float
    datetime: datetime.datetime

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PortfolioItem):
            raise NotImplementedError(
                f"Can't compare objects of type {type(other)} and {type(self)}"
            )
        return (
            self.symbol == other.symbol
            and self.market_value == other.market_value
            and self.quantity == other.quantity
            and self.datetime == other.datetime
        )


class PortfolioItemDifference(BaseModel):
    symbol: Symbol
    delta_market_value: float
    delta_quantity: float
    delta_datetime: datetime.timedelta


class PortfolioItemRatio(BaseModel):
    symbol: Symbol
    market_value_ratio: float
    quantity_ratio: float
    datetime_ratio_in_days: float

    @property
    def return_ratio(self) -> float:
        return self.market_value_ratio / self.quantity_ratio


class PortfolioRatio(BaseModel):
    items: list[PortfolioItemRatio]

    @property
    def portfolio_datetime_ratio_in_days(self) -> float:
        return self.items[0].datetime_ratio_in_days

    def __len__(self) -> int:
        return len(self.items)

    @field_validator("items", mode="before")
    @classmethod
    def datetime_must_be_same(
        cls, items: list[PortfolioItemRatio]
    ) -> list[PortfolioItemRatio]:
        if len(items) == 0:
            return items
        portfolio_datetime_ratio_in_days = items[0].datetime_ratio_in_days
        for item in items:
            if item.datetime_ratio_in_days != portfolio_datetime_ratio_in_days:
                raise ValueError(
                    "PortfolioItemRatio items should have same datetime_ratio"
                )
        return items

    def __getitem__(self, symbol: Symbol) -> PortfolioItemRatio:
        items = list(filter(lambda x: x.symbol == symbol, self.items))
        if items:
            return items[0]
        else:
            return PortfolioItemRatio(
                symbol=symbol,
                market_value_ratio=1,
                quantity_ratio=1,
                datetime_ratio_in_days=self.portfolio_datetime_ratio_in_days,
            )


class PortfolioDifference(BaseModel):
    items: list[PortfolioItemDifference]

    @property
    def portfolio_difference_delta_datetime(self) -> datetime.timedelta:
        return self.items[0].delta_datetime

    @field_validator("items", mode="before")
    @classmethod
    def datetime_must_be_same(
        cls, items: list[PortfolioItemDifference]
    ) -> list[PortfolioItemDifference]:
        if len(items) == 0:
            return items
        portfolio_difference_datetime = items[0].delta_datetime
        for item in items:
            if item.delta_datetime != portfolio_difference_datetime:
                raise ValueError(
                    "PortfolioDifference items should have same delta_datetime"
                )
        return items

    def __getitem__(self, symbol: Symbol) -> PortfolioItemDifference:
        items = list(filter(lambda x: x.symbol == symbol, self.items))
        if items:
            return items[0]
        else:
            return PortfolioItemDifference(
                symbol=symbol,
                delta_market_value=0,
                delta_quantity=0,
                delta_datetime=self.portfolio_difference_delta_datetime,
            )


class Portfolio(BaseModel):
    items: list[PortfolioItem]

    @field_validator("items", mode="before")
    @classmethod
    def datetime_must_be_same(
        cls, items: list[PortfolioItem]
    ) -> list[PortfolioItem]:
        if len(items) == 0:
            raise ValueError("Portfolio cannot be empty!")
        portfolio_datetime = items[0].datetime
        for item in items:
            if item.datetime != portfolio_datetime:
                raise ValueError("Portfolio items should be in same datetime")
        return items

    @property
    def portfolio_datetime(self) -> datetime.datetime:
        return self.items[0].datetime

    def __getitem__(self, symbol: Symbol) -> PortfolioItem:
        items = list(filter(lambda x: x.symbol == symbol, self.items))
        if items:
            return items[0]
        else:
            return PortfolioItem(
                symbol=symbol,
                market_value=0,
                quantity=0,
                datetime=self.portfolio_datetime,
            )

    def __sub__(self, other: "Portfolio") -> PortfolioDifference:
        """Returns the difference between two portfolio"""
        items: list[PortfolioItemDifference] = []

        symbols = set(
            [self_item.symbol for self_item in self.items]
            + [other_item.symbol for other_item in other.items]
        )
        for symbol in symbols:
            self_item = self[symbol]
            other_item = other[symbol]
            items.append(
                PortfolioItemDifference(
                    symbol=symbol,
                    delta_market_value=self_item.market_value
                    - other_item.market_value,
                    delta_quantity=self_item.quantity - other_item.quantity,
                    delta_datetime=self_item.datetime - other_item.datetime,
                )
            )
        return PortfolioDifference(items=items)

    def __truediv__(self, other: "Portfolio") -> PortfolioRatio:
        """Returns the ratio of two portfolio"""
        items: list[PortfolioItemRatio] = []

        symbols = set(
            [self_item.symbol for self_item in self.items]
            + [other_item.symbol for other_item in other.items]
        )
        for symbol in symbols:
            self_item = self[symbol]
            other_item = other[symbol]
            items.append(
                PortfolioItemRatio(
                    symbol=symbol,
                    market_value_ratio=divide_with_no_zero_division_error(
                        self_item.market_value, other_item.market_value
                    ),
                    quantity_ratio=divide_with_no_zero_division_error(
                        self_item.quantity, other_item.quantity
                    ),
                    datetime_ratio_in_days=(
                        self_item.datetime - other_item.datetime
                    )
                    / datetime.timedelta(days=1),
                )
            )
        return PortfolioRatio(items=items)

    def __add__(self, other: PortfolioDifference) -> "Portfolio":
        """Returns a new portfolio"""
        items: list[PortfolioItem] = []

        symbols = set(
            [self_item.symbol for self_item in self.items]
            + [other_item.symbol for other_item in other.items]
        )
        for symbol in symbols:
            self_item = self[symbol]
            other_item = other[symbol]
            items.append(
                PortfolioItem(
                    symbol=symbol,
                    market_value=self_item.market_value
                    + other_item.delta_market_value,
                    quantity=self_item.quantity + other_item.delta_quantity,
                    datetime=self_item.datetime + other_item.delta_datetime,
                )
            )
        return Portfolio(items=items)
