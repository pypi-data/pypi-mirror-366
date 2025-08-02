from sqlalchemy.orm import Session

from xarizmi.models.exchange import Exchange as PyExchange

from ..models import Exchange


def upsert_exchange(exchange: PyExchange, session: Session) -> Exchange:
    """Creates exchange in db or returns it if it already exists"""
    db_exchange = (
        session.query(Exchange)
        .filter_by(
            name=exchange.name,
        )
        .first()
    )

    if not db_exchange:
        db_exchange = Exchange(
            name=exchange.name,
        )
        session.merge(db_exchange)
        session.flush()
        session.commit()
    return db_exchange


def bulk_upsert_exchanges(
    exchanges: list[PyExchange], session: Session
) -> list[Exchange]:
    db_exchanges = []
    for exchange in exchanges:
        db_exchange = upsert_exchange(exchange=exchange, session=session)
        db_exchanges.append(db_exchange)
    return db_exchanges
