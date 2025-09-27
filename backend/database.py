import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Import models after engine creation to avoid circular imports
import models

# Check if we're in development mode
DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "False").lower() == "true"

if DEVELOPMENT_MODE:
    # Use SQLite for development
    DATABASE_URL = "sqlite:///./cipherdrive_dev.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # SQLite specific
        echo=True  # Log SQL queries in development
    )
else:
    # Use PostgreSQL for production
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "postgresql://cipherdrive_user:cipherdrive_pass@db:5432/cipherdrive_db"
    )
    
    # Create engine with connection pooling
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=300
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    models.Base.metadata.create_all(bind=engine)