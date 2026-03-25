from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL_SQLITE = "sqlite:///./attendance_db.sqlite"

engine = create_engine(SQLALCHEMY_DATABASE_URL_SQLITE, connect_args={"check_same_thread": False})
print("[INFO] Using Local SQLite Database.")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
