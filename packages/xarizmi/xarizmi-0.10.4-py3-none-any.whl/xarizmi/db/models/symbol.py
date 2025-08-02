from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Computed
from sqlalchemy.schema import UniqueConstraint

from xarizmi.db.models.base import Base

from .constants import TableNamesEnum
from .exchange import Exchange


class Symbol(Base):  # type: ignore
    __tablename__ = TableNamesEnum.SYMBOL.value
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    base_currency: Mapped[str] = mapped_column(String, nullable=False)
    quote_currency: Mapped[str] = mapped_column(String, nullable=False)
    fee_currency: Mapped[str] = mapped_column(String, nullable=True)
    name: Mapped[str] = mapped_column(
        String, Computed("base_currency || '-' || quote_currency"), unique=True
    )
    exchange_name: Mapped[str] = mapped_column(
        String, ForeignKey(Exchange.name), nullable=False
    )

    # Establish a many-to-one relationship
    exchange: Mapped[Exchange] = relationship(
        "Exchange", back_populates="symbols"
    )

    candlesticks: Mapped[list["CandleStick"]] = relationship(  # type: ignore  # noqa: F821,E501
        "CandleStick", back_populates="symbol"
    )

    portfolio_items: Mapped[list["PortfolioItem"]] = relationship(  # type: ignore  # noqa: F821,E501
        "PortfolioItem", back_populates="symbol"
    )

    orders: Mapped[list["Order"]] = relationship(  # type: ignore  # noqa: F821,E501
        "Order", back_populates="symbol"
    )

    @property
    def symbol(self) -> str:
        return f"{self.base_currency}-{self.quote_currency}"

    __table_args__ = (
        UniqueConstraint(
            "base_currency",
            "quote_currency",
            "exchange_name",
            name="uix_symbol_name_exchange",
        ),
    )
