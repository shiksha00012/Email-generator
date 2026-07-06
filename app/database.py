from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# MySQL connection URL — loaded from .env
# Format: mysql+pymysql://user:password@host:port/dbname
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:password@localhost:3306/email_assistant"
)

engine = create_engine(
    DATABASE_URL,
    # Keep connections alive and recycle stale ones
    pool_pre_ping=True,
    pool_recycle=3600,          # recycle connections every hour
    pool_size=10,               # max persistent connections
    max_overflow=20,            # allow burst above pool_size
    echo=False,                 # set True to log every SQL query (debug)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class EmailHistory(Base):
    __tablename__ = "email_history"

    id            = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type          = Column(String(50),  nullable=False)   # compose | reply | tone | summary
    prompt_preview= Column(String(200), nullable=False)
    output        = Column(Text(length=65535), nullable=False)   # MySQL TEXT (64 KB)
    tone          = Column(String(50),  nullable=True)    # formal | professional | friendly | concise
    created_at    = Column(DateTime,    default=datetime.utcnow, nullable=False)


def init_db():
    """Create all tables if they don't already exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency — yields a DB session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
