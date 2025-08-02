from datetime import datetime

from sqlalchemy import desc
from sqlalchemy.orm import Session

from xarizmi.db.models.portfolio import PortfolioItem
from xarizmi.db.models.symbol import Symbol
from xarizmi.models.portfolio import Portfolio as PyPortfolio
from xarizmi.models.portfolio import PortfolioItem as PyPortfolioItem


def get_portfolio_items_between_dates(
    session: Session, start_date: datetime, end_date: datetime
) -> PyPortfolio:
    results = (
        session.query(
            PortfolioItem.market_value,
            PortfolioItem.quantity,
            PortfolioItem.datetime,
            Symbol.base_currency,
            Symbol.quote_currency,
            Symbol.fee_currency,
            Symbol.exchange_name,
        )
        .join(Symbol, PortfolioItem.symbol_id == Symbol.id)
        .filter(PortfolioItem.datetime.between(start_date, end_date))
        .order_by(desc(PortfolioItem.market_value))
    ).all()
    results = [item._asdict() for item in results]  # type: ignore

    return PyPortfolio(
        items=[
            PyPortfolioItem.model_validate(
                {
                    "symbol": {
                        "base_currency": {
                            "name": item["base_currency"],  # type: ignore
                        },
                        "quote_currency": {
                            "name": item["quote_currency"],  # type: ignore
                        },
                        "fee_currency": {
                            "name": item["fee_currency"],  # type: ignore
                        },
                        "exchange": {
                            "name": item["exchange_name"],  # type: ignore
                        },
                    },
                    "market_value": item["market_value"],  # type: ignore
                    "quantity": item["quantity"],  # type: ignore
                    "datetime": item["datetime"],  # type: ignore
                }
            )
            for item in results
        ]
    )
