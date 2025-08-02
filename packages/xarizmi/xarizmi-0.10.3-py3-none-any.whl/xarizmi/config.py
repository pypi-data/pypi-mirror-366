from typing import Any

from sqlalchemy import Engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Config:
    _NAME_DOJINESS_THRESHOLD = "DOJINESS_THRESHOLD"
    _NAME_DATABASE_URL = "DATABASE_URL"

    def __init__(self) -> None:
        self._settings: dict[str, int | float | str | None] = {}
        self.reset()

    def reset(self) -> None:
        self._settings[self._NAME_DOJINESS_THRESHOLD] = 0.95
        self.DATABASE_URL = "postgresql://postgres:1@localhost/xarizmi"

    @property
    def DOJINESS_THRESHOLD(self) -> float:
        return self._settings.get(Config._NAME_DOJINESS_THRESHOLD)  # type: ignore  # noqa: E501

    @DOJINESS_THRESHOLD.setter
    def DOJINESS_THRESHOLD(self, value: float) -> None:
        self._settings[Config._NAME_DOJINESS_THRESHOLD] = value

    @property
    def DATABASE_URL(self) -> str:
        return self._settings.get(Config._NAME_DATABASE_URL)  # type: ignore  # noqa: E501

    @DATABASE_URL.setter
    def DATABASE_URL(self, url: str) -> None:
        self._settings[Config._NAME_DATABASE_URL] = url
        self._db_engine = create_engine(url)
        self.session_maker = sessionmaker(bind=self._db_engine)

    @property
    def db_engine(self) -> Engine:
        return create_engine(self.DATABASE_URL)

    def update(self, **kwargs: Any) -> None:
        self._settings.update(kwargs)

    def get(self, key: str) -> int | float | str | None:
        return self._settings.get(key)


# Create a singleton instance of the Config class
config = Config()


def get_config() -> Config:
    global config
    return config


def reset_config() -> None:
    global config
    config.reset()
