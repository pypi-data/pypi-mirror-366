from typing import Self

from pydantic import BaseModel

from xarizmi.models.currency import Currency
from xarizmi.models.exchange import Exchange


class Symbol(BaseModel):
    base_currency: Currency
    quote_currency: Currency
    fee_currency: Currency
    exchange: Exchange | None = None

    def __hash__(self) -> int:
        return hash((self.base_currency.name, self.quote_currency.name))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Symbol):
            raise NotImplementedError(
                f"Can't compare objects of type {type(other)} and {type(self)}"
            )
        return (
            self.base_currency == other.base_currency
            and self.quote_currency == other.quote_currency
            and self.fee_currency == other.fee_currency
            and self.exchange == other.exchange
        )

    @classmethod
    def build(
        cls,
        base_currency: str,
        quote_currency: str,
        fee_currency: str,
        exchange: str | None = None,
    ) -> "Symbol":
        """
        Example
        -------
        >>> symbol = Symbol.build(
                base_currency="BTC",
                quote_currency="USD",
                fee_currency="USD",
                exchange="BINANCE",
            )
        """
        data = {
            "base_currency": {"name": base_currency},
            "quote_currency": {"name": quote_currency},
            "fee_currency": {"name": fee_currency},
        }
        if exchange is not None:
            data["exchange"] = {"name": exchange}
        return cls(**data)

    def to_string(self) -> str:
        """
        Example
        -------
        >>> symbol = Symbol.build(
                base_currency="BTC",
                quote_currency="USD",
                fee_currency="USD",
                exchange="BINANCE",
            )
        >>> symbol.to_string()
        'BTC-USD'
        """
        return (
            self.base_currency.to_string()
            + "-"
            + self.quote_currency.to_string()
        )

    def to_flat_csv(self) -> str:
        """
        Example
        -------
        >>> symbol = Symbol.build(
                base_currency="BTC",
                quote_currency="USD",
                fee_currency="USD",
                exchange="BINANCE",
            )
        >>> symbol.to_string()
        'BTC-USD'
        """
        return (
            self.base_currency.to_string()
            + "-"
            + self.quote_currency.to_string()
        )

    def to_dict(self) -> dict[str, str | None]:
        """
        Example
        -------
        >>> symbol = Symbol.build(
                base_currency="BTC",
                quote_currency="USD",
                fee_currency="USD",
                exchange="BINANCE",
            )
        >>> symbol.to_dict()
        {
            "base_currency": "BTC",
            "quote_currency": "USD",
            "fee_currency": "USD"
            "exchange": "BINANCE",
        }
        """
        return {
            "base_currency": self.base_currency.to_string(),
            "quote_currency": self.quote_currency.to_string(),
            "fee_currency": self.fee_currency.to_string(),
            "exchange": (
                self.exchange.to_string()
                if (self.exchange is not None)
                else None
            ),
        }


class SymbolList(BaseModel):
    items: list[Symbol] = []

    @classmethod
    def build(
        cls,
        items: list[dict[str, str]],
    ) -> Self:
        symbol_items = []
        for item in items:
            symbol_items.append(
                Symbol.build(
                    base_currency=item["base_currency"],
                    quote_currency=item["quote_currency"],
                    fee_currency=item["fee_currency"],
                    exchange=item["exchange"],
                )
            )
        return cls(items=symbol_items)
