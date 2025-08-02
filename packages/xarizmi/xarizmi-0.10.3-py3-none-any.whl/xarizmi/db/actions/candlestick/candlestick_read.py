from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import and_

from xarizmi.candlestick import Candlestick as PyCandleStick
from xarizmi.candlestick import CandlestickChart as PyCandlestickChart
from xarizmi.db.actions.symbol import get_symbol
from xarizmi.db.models.candlestick import CandleStick
from xarizmi.db.models.symbol import Symbol
from xarizmi.enums import IntervalTypeEnum
from xarizmi.models.symbol import Symbol as PySymbol


def get_filtered_candlesticks(
    session: Session,
    symbol: Optional[PySymbol] = None,
    start_datetime: Optional[datetime] = None,
    end_datetime: Optional[datetime] = None,
    filter_by_interval_type: IntervalTypeEnum | None = None,
    skip: int = 0,
    limit: int = 1000,
) -> PyCandlestickChart:

    # Base query
    query = select(
        CandleStick,  # All columns from CandleStick
        Symbol.name.label("symbol_name"),  # Symbol name with alias
    ).join(
        Symbol, CandleStick.symbol_id == Symbol.id
    )  # Join with Symbol

    # Add filters
    filters = []
    if symbol:
        filters.append(
            Symbol.id == get_symbol(symbol=symbol, session=session).id
        )
    if start_datetime:
        filters.append(CandleStick.datetime >= start_datetime)
    if end_datetime:
        filters.append(CandleStick.datetime <= end_datetime)
    if filter_by_interval_type:
        filters.append(CandleStick.interval_type == filter_by_interval_type)

    if filters:
        query = query.where(and_(*filters))

    # Add ordering, skip, and limit for pagination
    query = (
        query.order_by(CandleStick.datetime.asc()).offset(skip).limit(limit)
    )

    # Execute the query
    result: list[CandleStick] = [
        item.CandleStick for item in session.execute(query).all()
    ]

    return PyCandlestickChart(
        candles=[
            PyCandleStick(
                open=db_candlestick.open,
                close=db_candlestick.close,
                low=db_candlestick.low,
                high=db_candlestick.high,
                volume=db_candlestick.volume,
                amount=db_candlestick.amount,
                interval_type=db_candlestick.interval_type,
                interval=db_candlestick.interval,
                symbol=symbol,
                datetime=db_candlestick.datetime,
                exchange=None,
            )
            for db_candlestick in result
        ]
    )
