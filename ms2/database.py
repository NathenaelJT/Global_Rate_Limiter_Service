from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

# Connect to a local SQLite file named sql_app.db
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# check_same_thread=False is required for SQLite.
# timeout=15 tells SQLite to wait up to 15 seconds if the database is
# currently locked.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 15},
)


# Enable WAL (Write-Ahead Logging) mode.
# This vastly improves SQLite handling concurrent reads/writes from workers!
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()


# A SessionLocal class will act as a factory for our database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our models
Base = declarative_base()


# Dependency function to get a database connection per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
