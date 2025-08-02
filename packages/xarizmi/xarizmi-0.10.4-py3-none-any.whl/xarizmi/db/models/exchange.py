from typing import Self

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship

from xarizmi.db.models.base import Base
from xarizmi.models.exchange import Exchange as PyExchange

from .constants import TableNamesEnum


class Exchange(Base):  # type: ignore
    __tablename__ = TableNamesEnum.EXCHANGE.value
    name = Column(String, primary_key=True, unique=True)

    symbols: Mapped[list["Symbol"]] = relationship(  # type: ignore  # noqa: F821,E501
        "Symbol", back_populates="exchange"
    )

    def to_pydantic(self) -> PyExchange:
        return PyExchange(name=self.name)

    @classmethod
    def from_pydantic(cls, exchange: PyExchange) -> Self:
        return cls(name=exchange)
