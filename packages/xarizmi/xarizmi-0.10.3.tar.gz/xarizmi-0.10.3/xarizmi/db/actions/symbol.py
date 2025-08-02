from sqlalchemy.orm import Session

from xarizmi.models.symbol import Symbol as PySymbol

from ..models import Symbol


def get_symbol(symbol: PySymbol, session: Session) -> Symbol:
    db_symbol = (
        session.query(Symbol)
        .filter_by(
            base_currency=symbol.base_currency.name,
            quote_currency=symbol.quote_currency.name,
            exchange_name=symbol.exchange.name,  # type: ignore
        )
        .first()
    )
    if db_symbol is None:
        raise RuntimeError("couldn't find the symbol in DB table!")
    return db_symbol


def upsert_symbol(symbol: PySymbol, session: Session) -> Symbol:
    """Creates symbol in db or returns it if it already exists"""
    db_symbol = (
        session.query(Symbol)
        .filter_by(
            base_currency=symbol.base_currency.name,
            quote_currency=symbol.quote_currency.name,
            exchange_name=symbol.exchange.name,  # type: ignore
        )
        .first()
    )

    if not db_symbol:
        db_symbol = Symbol(
            base_currency=symbol.base_currency.name,
            quote_currency=symbol.quote_currency.name,
            fee_currency=symbol.fee_currency.name,
            exchange_name=symbol.exchange.name,  # type: ignore
        )
        session.merge(db_symbol)
        session.flush()
    return db_symbol


def bulk_upsert_symbols(
    symbols: list[PySymbol], session: Session
) -> list[Symbol]:
    db_symbols = []
    for symbol in symbols:
        db_symbol = upsert_symbol(symbol, session=session)
        db_symbols += [db_symbol]
    return db_symbols
