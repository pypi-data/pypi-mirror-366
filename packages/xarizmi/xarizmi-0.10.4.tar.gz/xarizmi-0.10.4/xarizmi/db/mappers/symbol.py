from typing import TypedDict

from sqlalchemy.orm import Session

from xarizmi.db.client import session_scope
from xarizmi.db.mappers.base import PydanticModelDbMapper
from xarizmi.db.models.symbol import Symbol as SqlAlchemySymbol
from xarizmi.models.currency import Currency
from xarizmi.models.exchange import Exchange as PydanticExchange
from xarizmi.models.symbol import Symbol as PydanticSymbol


class SYMBOL_FLAT_TYPED_DICT(TypedDict):
    base_currency: str
    quote_currency: str
    fee_currency: str
    exchange: str


class SymbolDbMapper(PydanticModelDbMapper):
    PRIMARY_KEY_FIELD = ["id"]
    COMPUTED_FIELD_KEYS = ["name"]

    def __init__(self, obj: SqlAlchemySymbol | PydanticSymbol) -> None:
        super().__init__(
            pydantic_class=PydanticSymbol, sqlalchemy_class=SqlAlchemySymbol
        )
        self._refresh(obj)

    @property
    def pydantic_obj(self) -> PydanticSymbol:
        return self._pydantic_obj  # type: ignore

    @property
    def sqlalchemy_obj(self) -> SqlAlchemySymbol:
        return self._sqlalchemy_obj  # type: ignore

    def _to_pydantic(self, obj: SqlAlchemySymbol) -> PydanticSymbol:  # type: ignore  # noqa: E501
        return PydanticSymbol(
            base_currency=Currency(name=str(obj.base_currency)),
            quote_currency=Currency(name=str(obj.quote_currency)),
            fee_currency=Currency(name=str(obj.fee_currency)),
            exchange_name=PydanticExchange(name=str(obj.exchange_name)),
        )

    def _to_sqlalchemy(self, obj: PydanticSymbol) -> SqlAlchemySymbol:  # type: ignore  # noqa: E501
        return SqlAlchemySymbol(
            base_currency=obj.base_currency.name,
            quote_currency=obj.quote_currency.name,
            fee_currency=obj.fee_currency.name,
            exchange_name=obj.exchange.name,  # type: ignore
        )

    def _does_exist_in_session(self, session: Session) -> bool:
        record = (
            session.query(SqlAlchemySymbol)
            .filter_by(
                base_currency=self.sqlalchemy_obj.base_currency,
                quote_currency=self.sqlalchemy_obj.quote_currency,
            )
            .first()
        )
        if record is None:
            return False
        else:
            return True

    def get(self, session: None | Session = None) -> SqlAlchemySymbol | None:
        return super().get(session=session)  # type: ignore

    def _get_in_session(self, session: Session) -> SqlAlchemySymbol | None:  # type: ignore  # noqa: E501
        record = (
            session.query(SqlAlchemySymbol)
            .filter_by(
                base_currency=self.sqlalchemy_obj.base_currency,
                quote_currency=self.sqlalchemy_obj.quote_currency,
                exchange_name=self.sqlalchemy_obj.exchange_name,
            )
            .first()
        )
        return record

    def _upsert_in_session(self, session: Session) -> None:
        record = self._get_in_session(session=session)
        if record:
            for key in self.sqlalchemy_obj.__table__.columns.keys():
                if key not in (
                    SymbolDbMapper.PRIMARY_KEY_FIELD
                    + SymbolDbMapper.COMPUTED_FIELD_KEYS
                ):  # Exclude primary key and computed keys from updates
                    setattr(record, key, getattr(self.sqlalchemy_obj, key))
        else:
            session.merge(self.sqlalchemy_obj)

    def upsert(self, session: Session | None = None) -> None:
        if session is None:
            with session_scope() as session:
                self._upsert_in_session(session=session)
        else:
            self._upsert_in_session(session=session)

    @staticmethod
    def bulk_upsert_from_data(
        data_list: list[SYMBOL_FLAT_TYPED_DICT], session: Session | None = None
    ) -> None:
        """
        data_list should be like this
        [
            {
                "base_currency": "BTC",
                "quote_currency": "USDT",
                "fee_currency": "USDT",
                "exchange_name": "BINANCE",
            },
            ...
        ]
        """
        symbol_dbs: list[SymbolDbMapper] = []
        for item in data_list:
            symbol_dbs.append(SymbolDbMapper(PydanticSymbol.build(**item)))
        if session is None:
            with session_scope() as session:
                for symbol_db in symbol_dbs:
                    symbol_db.upsert(session=session)
        else:
            for symbol_db in symbol_dbs:
                symbol_db.upsert(session=session)
