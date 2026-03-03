from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker

# Use SQLite for testing - hardcoded, no env file!
DATABASE_URL = "sqlite:///./todo.db"

# Create engine for SQLite
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session
)

# Create tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    print("✅ Database tables created")

# Get database session
def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
