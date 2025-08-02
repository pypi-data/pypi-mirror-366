from sqlalchemy.orm import Session

from xarizmi.db.models.order import Order
from xarizmi.enums import OrderStatusEnum
from xarizmi.models import Symbol as PySymbol

from .read import get_unique_order_in_db


def delete_unique_order(
    session: Session,
    symbol: PySymbol,
    order_id: str,
) -> None:
    db_order = get_unique_order_in_db(
        session=session, symbol=symbol, order_id=order_id
    )
    session.delete(db_order)


def delete_all_cancelled_orders(
    session: Session,
) -> None:
    session.query(Order).where(
        Order.status == OrderStatusEnum.CANCELLED
    ).delete()
