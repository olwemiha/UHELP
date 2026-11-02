# database.py
from pathlib import Path

from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_PATH = Path(__file__).resolve().parent / "eduaccess.db"
SQLALCHEMY_DATABASE_URL = URL.create("sqlite", database=str(DATABASE_PATH))

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def initialize_schema():
    Base.metadata.create_all(bind=engine)

    programme_columns = {
        column["name"] for column in inspect(engine).get_columns("programmes")
    }
    if "score_type" not in programme_columns:
        with engine.begin() as connection:
            connection.exec_driver_sql(
                "ALTER TABLE programmes ADD COLUMN score_type VARCHAR"
            )