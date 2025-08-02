from pydantic import BaseModel

from xarizmi.enums import OrderStatusEnum
from xarizmi.enums import SideEnum

from .symbol import Symbol


class Order(BaseModel):
    symbol: Symbol
    price: float
    amount: float
    status: OrderStatusEnum
    side: SideEnum
    # order_id only exists when order is put in place in a trading platform
    # but to work with orders you don't need to have order_id necessarily
    order_id: str | None = None

    @classmethod
    def build_from_currencies(
        cls,
        base_currency: str,
        quote_currency: str,
        fee_currency: str,
        order_id: str,
        price: float,
        amount: float,
        status: OrderStatusEnum,
        side: SideEnum,
        exchange: str | None = None,
    ) -> "Order":

        symbol = Symbol.build(
            base_currency=base_currency,
            quote_currency=quote_currency,
            fee_currency=fee_currency,
            exchange=exchange,
        )
        data = {
            "symbol": symbol,
            "order_id": order_id,
            "price": price,
            "amount": amount,
            "side": side,
            "status": status,
        }
        return cls(**data)
