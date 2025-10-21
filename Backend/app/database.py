from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from typing import Generator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./criminal_law_kb.db"
)

# Create engine
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration for development
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False  # Set to True for SQL query logging
    )
else:
    # PostgreSQL configuration for production
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database with tables"""
    try:
        # Import all models to ensure they are registered
        from app.models.law_models import Base
        from app.models.contact_models import ContactMessage
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully")
        
    except Exception as e:
        print(f"Database initialization failed: {e}")
        raise

def get_db_stats():
    """Get basic database statistics"""
    try:
        db = SessionLocal()
        
        # Count records in main tables
        from app.models.law_models import LawSection, LegalCase, SearchQuery
        
        section_count = db.query(LawSection).count()
        case_count = db.query(LegalCase).count()
        query_count = db.query(SearchQuery).count()
        
        db.close()
        
        return {
            "total_sections": section_count,
            "total_cases": case_count,
            "total_searches": query_count,
            "database_url": DATABASE_URL
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "database_url": DATABASE_URL
        }

def test_connection():
    """Test database connection"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False

if __name__ == "__main__":
    # Test database connection and initialization
    print("Testing database connection...")
    if test_connection():
        print("Database connection successful!")
        
        print("Initializing database...")
        init_db()
        
        print("Getting database stats...")
        stats = get_db_stats()
        print(f"Database stats: {stats}")
    else:
        print("Database connection failed!")
