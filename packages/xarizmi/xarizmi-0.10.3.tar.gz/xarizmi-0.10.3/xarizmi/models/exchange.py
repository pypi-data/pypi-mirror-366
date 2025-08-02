from pydantic import BaseModel


class Exchange(BaseModel):
    name: str

    def to_string(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Exchange):
            raise NotImplementedError(
                f"Can't compare objects of type {type(other)} and {type(self)}"
            )
        return self.name == other.name


class ExchangeList(BaseModel):
    items: list[Exchange]
