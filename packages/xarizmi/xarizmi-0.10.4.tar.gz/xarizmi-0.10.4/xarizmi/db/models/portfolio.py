from datetime import datetime as dt

from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint

from xarizmi.db.models.base import Base

from .constants import TableNamesEnum
from .symbol import Symbol


class PortfolioItem(Base):  # type: ignore
    __tablename__ = TableNamesEnum.PORTFOLIO_ITEM.value
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    symbol_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Symbol.id), nullable=False
    )
    symbol: Mapped[Symbol] = relationship(
        "Symbol", back_populates="portfolio_items"
    )

    market_value: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    datetime: Mapped[dt] = mapped_column(
        DateTime,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "symbol_id",
            "datetime",
            name="uix_symbol_datetime",
        ),
    )
