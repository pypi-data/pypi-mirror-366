from abc import ABC
from abc import abstractmethod
from typing import Type

from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy.orm import DeclarativeBase as SqlAlchemyBaseModel
from sqlalchemy.orm import Session

from xarizmi.db.client import session_scope
from xarizmi.db.models.symbol import Symbol as SqlAlchemySymbol


class PydanticModelDbMapper(ABC):

    def __init__(
        self,
        pydantic_class: Type[PydanticBaseModel],
        sqlalchemy_class: Type[SqlAlchemyBaseModel],
    ) -> None:
        self._pydantic_class = pydantic_class
        self._sqlalchemy_class = sqlalchemy_class

    def _refresh(self, obj: PydanticBaseModel | SqlAlchemyBaseModel) -> None:
        if isinstance(obj, self._sqlalchemy_class):
            self._sqlalchemy_obj = obj
            self._pydantic_obj = self._to_pydantic(obj)
        elif isinstance(obj, self._pydantic_class):
            self._sqlalchemy_obj = self._to_sqlalchemy(obj)
            self._pydantic_obj = obj

    @abstractmethod
    def _to_pydantic(self, obj: SqlAlchemyBaseModel) -> PydanticBaseModel: ...

    @abstractmethod
    def _to_sqlalchemy(self, obj: PydanticBaseModel) -> SqlAlchemySymbol: ...

    @abstractmethod
    def _get_in_session(
        self, session: Session | None = None
    ) -> SqlAlchemySymbol | None: ...

    def get(
        self, session: None | Session = None
    ) -> SqlAlchemyBaseModel | None:
        if session is None:
            with session_scope() as session:
                record = self._get_in_session(session=session)
        else:
            record = self._get_in_session(session=session)
        return record

    def _does_exist_in_session(self, session: Session) -> bool:
        record = self._get_in_session(session=session)
        if record is None:
            return False
        else:
            return True
