from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

# Get database URL from settings
db_url = settings.DATABASE_URL

# Handle the postgres:// to postgresql:// conversion needed for some services like Render
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Set connection arguments based on database type
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}  # Only needed for SQLite

# Create engine with appropriate settings
engine = create_engine(
    db_url,
    echo=settings.ECHO,
    connect_args=connect_args,
    # Optional PostgreSQL-specific settings (uncomment if needed)
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
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
