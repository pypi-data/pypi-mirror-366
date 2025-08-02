from sqlalchemy.orm import Session

from xarizmi.candlestick import Candlestick as pyCandlestick
from xarizmi.db.models.candlestick import CandleStick


def upsert_candlestick(
    candlestick: pyCandlestick, symbol_id: int, session: Session
) -> CandleStick:
    """Creates candlestick in db or returns it if it already exists"""
    db_candlestick = (
        session.query(CandleStick)
        .filter_by(
            symbol_id=symbol_id,
            interval_type=candlestick.interval_type,
            interval=candlestick.interval,
        )
        .first()
    )

    if db_candlestick:
        db_candlestick.open = candlestick.open
        db_candlestick.close = candlestick.close
        db_candlestick.low = candlestick.low
        db_candlestick.high = candlestick.high
        db_candlestick.volume = candlestick.volume
        db_candlestick.amount = candlestick.amount  # type: ignore
        db_candlestick.datetime = candlestick.datetime  # type: ignore
    else:
        db_candlestick = CandleStick(
            symbol_id=symbol_id,
            open=candlestick.open,
            close=candlestick.close,
            high=candlestick.high,
            low=candlestick.low,
            datetime=candlestick.datetime,
            interval=candlestick.interval,
            interval_type=candlestick.interval_type,
            volume=candlestick.volume,
            amount=candlestick.amount,
        )
        session.merge(db_candlestick)
    session.commit()
    return db_candlestick
