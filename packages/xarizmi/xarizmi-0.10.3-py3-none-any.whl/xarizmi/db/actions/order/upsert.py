from sqlalchemy.orm import Session

from xarizmi.db.actions.symbol import get_symbol
from xarizmi.db.models.order import Order
from xarizmi.models.orders import Order as PyOrder


def upsert_order(
    order: PyOrder, session: Session, symbol_id: int | None = None
) -> Order:
    """Creates order in db or returns it if it already exists"""
    if symbol_id is None:
        symbol_id = get_symbol(order.symbol, session=session).id
    db_order = (
        session.query(Order)
        .filter_by(
            symbol_id=symbol_id,
            order_id=order.order_id,
        )
        .first()
    )

    if db_order:
        db_order.amount = order.amount
        db_order.price = order.price
        db_order.status = order.status
        db_order.side = order.side
    else:
        db_order = Order(
            symbol_id=symbol_id,
            order_id=order.order_id,
            price=order.price,
            amount=order.amount,
            status=order.status,
            side=order.side,
        )
        session.merge(db_order)
    session.commit()
    return db_order
