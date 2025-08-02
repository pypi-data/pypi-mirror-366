from sqlalchemy import Enum
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint

from xarizmi.db.models.base import Base
from xarizmi.enums import OrderStatusEnum
from xarizmi.enums import SideEnum

from .constants import TableNamesEnum
from .symbol import Symbol


class Order(Base):  # type: ignore
    __tablename__ = TableNamesEnum.ORDER.value
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    symbol_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Symbol.id), nullable=False
    )
    symbol: Mapped[Symbol] = relationship("Symbol", back_populates="orders")

    order_id: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    side: Mapped[str] = mapped_column(
        Enum(SideEnum, name="side_enum", create_type=True),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        Enum(OrderStatusEnum, name="order_status_enum", create_type=True),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "symbol_id",
            "order_id",
            name="uix_symbol_id_order_id",
        ),
    )
