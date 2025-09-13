import os
from sqlalchemy import create_engine, text

SQL_PATH = "/app/database/migrations/versions/0001_init.sql"
DATABASE_URL = os.getenv("DATABASE_URL","postgresql+psycopg://dmf:dmf@postgres:5432/dmf")

def upgrade():
    engine = create_engine(DATABASE_URL, future=True)
    with engine.begin() as conn:
        with open(SQL_PATH, "r", encoding="utf-8") as f:
            conn.execute(text(f.read()))

if __name__ == "__main__":
    upgrade()
