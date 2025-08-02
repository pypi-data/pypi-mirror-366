from pathlib import Path

from alembic import command
from alembic.config import Config

from xarizmi.config import get_config

PARENT_DIR = Path(__file__).parent
alembic_ini = PARENT_DIR / "alembic.ini"


def run_db_migration() -> None:
    # Path to alembic.ini file
    alembic_cfg = Config(alembic_ini)

    # Dynamically set the database URL in Alembic's config
    alembic_cfg.set_main_option("sqlalchemy.url", get_config().DATABASE_URL)
    alembic_cfg.set_main_option(
        "script_location", (PARENT_DIR / "alembic").__str__()
    )

    command.upgrade(alembic_cfg, "head")
