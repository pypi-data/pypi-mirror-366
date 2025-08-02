from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import and_

from xarizmi.db.actions.symbol import get_symbol
from xarizmi.db.models.order import Order
from xarizmi.enums import OrderStatusEnum
from xarizmi.enums import SideEnum
from xarizmi.models import Symbol as PySymbol
from xarizmi.models.orders import Order as PyOrder


def get_unique_order_in_db(
    session: Session,
    symbol: PySymbol,
    order_id: str,
) -> Order | None:
    query = select(
        Order,  # All columns from Order
    )

    # Add filters
    filters = []
    db_symbol = get_symbol(symbol=symbol, session=session)
    filters.append(Order.symbol_id == db_symbol.id)
    filters.append(Order.order_id == order_id)

    if filters:
        query = query.where(and_(*filters))

    result = session.execute(query).one_or_none()
    if result:
        return result._asdict()["Order"]  # type: ignore
    else:
        return None


def get_unique_order(
    session: Session,
    symbol: PySymbol,
    order_id: str,
) -> PyOrder | None:
    db_order = get_unique_order_in_db(
        session=session, symbol=symbol, order_id=order_id
    )
    if db_order:
        return PyOrder(
            symbol=symbol,
            order_id=db_order.order_id,
            price=db_order.price,
            amount=db_order.amount,
            side=db_order.side,
            status=db_order.status,
        )
    else:
        return None


def get_orders(
    session: Session,
    symbol: PySymbol,
    filter_by_status: list[OrderStatusEnum] | None = None,
    filter_by_side: SideEnum | None = None,
) -> list[PyOrder]:
    query = select(
        Order,  # All columns from Order
    )

    # Add filters
    filters = []
    db_symbol = get_symbol(symbol=symbol, session=session)
    filters.append(Order.symbol_id == db_symbol.id)
    if filter_by_side:
        filters.append(Order.side == filter_by_side)
    if filter_by_status:
        filters.append(Order.status.in_(filter_by_status))

    if filters:
        query = query.where(and_(*filters))

    db_orders: list[Order] = [
        item._asdict()["Order"] for item in session.execute(query).all()
    ]

    return [
        PyOrder(
            symbol=symbol,
            order_id=db_order.order_id,
            price=db_order.price,
            amount=db_order.amount,
            side=db_order.side,
            status=db_order.status,
        )
        for db_order in db_orders
    ]


def get_active_orders(
    session: Session,
    symbol: PySymbol,
    filter_by_side: SideEnum | None = None,
) -> list[PyOrder]:
    return get_orders(
        session=session,
        symbol=symbol,
        filter_by_status=[
            OrderStatusEnum.ACTIVE,
            OrderStatusEnum.PARTIALLY_FILLED,
        ],
        filter_by_side=filter_by_side,
    )
