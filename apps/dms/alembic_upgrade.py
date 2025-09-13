import os
from pathlib import Path
from sqlalchemy import create_engine, text


DEFAULT_SQL_PATH = (
    Path(__file__).resolve().parents[2]
    / "database"
    / "migrations"
    / "versions"
    / "0001_init.sql"
)
SQL_PATH = Path(os.getenv("SQL_PATH", DEFAULT_SQL_PATH))

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://dmf:dmf@postgres:5432/dmf"
)


def upgrade():
    engine = create_engine(DATABASE_URL, future=True)
    with engine.begin() as conn:
        with SQL_PATH.open("r", encoding="utf-8") as f:
            conn.execute(text(f.read()))


if __name__ == "__main__":
    upgrade()
