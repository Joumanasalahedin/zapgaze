from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required. "
        "Set it to a PostgreSQL connection string, e.g., "
        "postgresql://user:password@host:5432/database"
    )

if not (
    DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("postgres://")
):
    raise ValueError(
        f"DATABASE_URL must be a PostgreSQL connection string. "
        f"Got: {DATABASE_URL[:50]}..."
    )

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
