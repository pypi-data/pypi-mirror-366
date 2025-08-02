from datetime import datetime as dt

from sqlalchemy import BigInteger
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint

from xarizmi.db.models.base import Base
from xarizmi.enums import IntervalTypeEnum

from .constants import TableNamesEnum
from .symbol import Symbol


class CandleStick(Base):  # type: ignore
    __tablename__ = TableNamesEnum.CANDLESTICK.value
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    symbol_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Symbol.id), nullable=False
    )
    symbol: Mapped[Symbol] = relationship(
        "Symbol", back_populates="candlesticks"
    )

    close: Mapped[float] = mapped_column(Float, nullable=False)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=True)
    interval_type: Mapped[str] = mapped_column(
        Enum(IntervalTypeEnum, name="interval_type_enum", create_type=True),
        nullable=False,
    )
    interval: Mapped[int] = mapped_column(BigInteger, nullable=True)
    datetime: Mapped[dt] = mapped_column(
        DateTime,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "symbol_id",
            "interval_type",
            "interval",
            name="uix_symbol_interval",
        ),
    )
