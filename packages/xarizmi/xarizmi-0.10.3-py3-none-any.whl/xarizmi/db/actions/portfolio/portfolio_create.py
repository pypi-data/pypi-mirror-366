from sqlalchemy.orm import Session

from xarizmi.db.actions.symbol import get_symbol
from xarizmi.db.models.portfolio import PortfolioItem
from xarizmi.models.portfolio import Portfolio as PyPortfolio
from xarizmi.models.portfolio import PortfolioItem as PyPortfolioItem


def upsert_portfolio_item(
    portfolio_item: PyPortfolioItem, session: Session
) -> PortfolioItem:
    """Creates portfolio_item in db or update and returns it if it already
    exists"""
    symbol = get_symbol(symbol=portfolio_item.symbol, session=session)
    db_portfolio_item = (
        session.query(PortfolioItem)
        .filter_by(
            datetime=portfolio_item.datetime,
            symbol_id=symbol.id,
        )
        .first()
    )

    if not db_portfolio_item:
        db_portfolio_item = PortfolioItem(
            symbol_id=symbol.id,
            market_value=portfolio_item.market_value,
            quantity=portfolio_item.quantity,
            datetime=portfolio_item.datetime,
        )
        session.merge(db_portfolio_item)
        session.flush()
    else:
        db_portfolio_item.quantity = portfolio_item.market_value
        db_portfolio_item.market_value = portfolio_item.market_value

    session.commit()
    return db_portfolio_item


def bulk_upsert_portfolio_item(
    portfolio_items: list[PyPortfolioItem], session: Session
) -> list[PortfolioItem]:
    db_portfolio_items = []
    for portfolio_item in portfolio_items:
        db_portfolio_item = upsert_portfolio_item(
            portfolio_item=portfolio_item, session=session
        )
        db_portfolio_items.append(db_portfolio_item)
    return db_portfolio_items


def upsert_portfolio(
    portfolio: PyPortfolio, session: Session
) -> list[PortfolioItem]:
    return bulk_upsert_portfolio_item(
        portfolio_items=portfolio.items, session=session
    )
