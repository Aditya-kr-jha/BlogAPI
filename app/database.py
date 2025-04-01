from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

connect_args = {"check_same_thread": False}
engine = create_engine(
    settings.DATABASE_URL, echo=settings.ECHO, connect_args=connect_args
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Creates a new session for each request and closes it after the request is processed.
    """
    print("Creating a new session")
    with Session(engine) as session:
        yield session
