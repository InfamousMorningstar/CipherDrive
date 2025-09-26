import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import logging
from typing import Generator

logger = logging.getLogger(__name__)

# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://dropboxuser:dropboxpass@localhost:5432/dropboxlite")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    pool_pre_ping=True,
    echo=os.getenv("SQL_DEBUG", "false").lower() == "true"
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

def get_database() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def init_database():
    """
    Initialize database tables
    """
    try:
        # Import models here to avoid circular imports
        from .models import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def check_database_connection() -> bool:
    """
    Check if database connection is working
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False