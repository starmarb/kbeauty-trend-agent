"""Initialize database tables."""
from src.models.schemas import Base
from src.db import engine


def init_database():
    """Create all tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def drop_database():
    """Drop all tables (use with caution!)."""
    print("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    print("Database tables dropped!")


if __name__ == "__main__":
    init_database()