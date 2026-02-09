# database.py
from sqlmodel import create_engine, Session, SQLModel
from pathlib import Path

DB_DIR = Path("data")
DB_DIR.mkdir(exist_ok=True)
DB_FILE = DB_DIR / "mini_siem.db"
DATABASE_URL = f"sqlite:///{DB_FILE}"

# echo=True for SQL output during development (optional)
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

def create_db_and_tables():
    from models import LogEvent  # import here to avoid circular import
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session